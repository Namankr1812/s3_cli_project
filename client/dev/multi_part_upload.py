import click
import boto3
import os
import time
import math
import datetime
import uuid
import logging
import hashlib
import sys
import cryptography
from botocore.exceptions import NoCredentialsError
from concurrent.futures import ThreadPoolExecutor, as_completed
from click import prompt
from tabulate import tabulate
from boto3.s3.transfer import TransferConfig
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json

session = boto3.Session()
s3 = session.resource('s3')

# Dictionary to store encryption keys for each file
encryption_keys = {}


def load_encryption_keys():
    try:
        with open('encryption_keys.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_encryption_keys():
    try:
        with open('encryption_keys.json', 'w') as file:
            keys_dict = {key: encryption_keys[key].decode('latin1') for key in encryption_keys}
            json.dump(keys_dict, file)
    except Exception as e:
        print(f"Error saving encryption keys: {e}")


def get_s3_endpoint(bucket_name):
    try:
        client = boto3.client('s3')
        location = client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        return f'https://s3.{location}.amazonaws.com'
    except Exception as e:
        print(f"Error getting S3 endpoint: {e}")
        return 'https://s3.amazonaws.com'  # Default to global S3 endpoint


def calculate_number_of_parts(file_size, part_size):
    return (file_size + part_size - 1) // part_size


def encrypt_data(data, encryption_key):
    salt = b'salt_123'  # Change this to a unique value
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        iterations=100000,
        salt=salt,
        length=32,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(encryption_key))
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data)
    return encrypted_data, key  # Return the encrypted data along with the key


def decrypt_data(data, encryption_key):
    try:
        cipher = Fernet(encryption_key)
        decrypted_data = cipher.decrypt(data)
        return decrypted_data
    except Exception as e:
        click.echo(f"Error decrypting data: {str(e)}")
        return b''  # Return an empty byte string in case of decryption failure


def generate_encryption_key():
    return os.urandom(32)


def upload_part(args, bucket_region='us-east-1'):
    part_number, upload_id, file_path, bucket, file_name, part_size = args
    s3_endpoint = get_s3_endpoint(bucket)

    with open(file_path, 'rb') as file:
        file.seek(part_size * (part_number - 1))
        data = file.read(part_size)

        # Retrieve or generate encryption key for the file
        encryption_key = encryption_keys.get(file_name)
        if not encryption_key:
            encryption_key = generate_encryption_key()
            encryption_keys[file_name] = encryption_key

        # Check if client-side encryption is enabled
        if encryption_key:
            encrypted_data, key = encrypt_data(data, encryption_key)
            encryption_keys[file_name] = key  # Update the key in case it was newly generated
        else:
            encrypted_data = data

        # Specify the server-side encryption algorithm
        s3 = boto3.client('s3', endpoint_url=s3_endpoint, region_name=bucket_region)

        # Use 'Body' directly in the arguments
        s3_upload_args = {
            'Bucket': bucket,
            'Key': file_name,
            'UploadId': upload_id,
            'PartNumber': part_number,
            'Body': encrypted_data,
        }

        try:
            response = s3.upload_part(**s3_upload_args)
        except Exception as e:
            click.echo(f"An error occurred: {str(e)}")
            return {"PartNumber": part_number, "Error": str(e)}

    etag = response["ETag"]
    return {"PartNumber": part_number, "ETag": etag}


@click.option("--target-part-size", default=None, type=int, help="Size of each part in bytes")
@click.option("--num-parts", default=None, type=int, help="Number of parts for each file")
def upload_folder(folder_path, bucket, target_part_size=None, num_parts=None):
    try:
        # Get S3 bucket region
        s3_bucket = boto3.resource('s3').Bucket(bucket)
        bucket_region = s3_bucket.meta.client.meta.region_name

        # Use the correct S3 endpoint for the specified region
        s3_endpoint = get_s3_endpoint(bucket)

        # Upload files in the folder
        s3 = boto3.client('s3', endpoint_url=s3_endpoint, region_name=bucket_region)
        parts_total = []

        # Get a list of all files in the folder
        file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if
                      os.path.isfile(os.path.join(folder_path, file))]

        # Prompt the user for the number of parts and part size
        if target_part_size is None or num_parts is None:
            total_file_size = sum(os.path.getsize(file) for file in file_paths)

            # Calculate the default part size based on file size
            default_part_size = min(max(5 * 1024 * 1024, total_file_size // 100), 100 * 1024 * 1024)
            click.echo(f"Default part size: {default_part_size} bytes")

            # Prompt the user for part size if not provided
            target_part_size = click.prompt("Enter part size (in bytes)", default=default_part_size, type=int)

            # Ensure the part size meets the minimum requirement
            target_part_size = max(target_part_size, 5 * 1024 * 1024)

            # Prompt the user for the number of parts if not provided
            num_parts = click.prompt("Enter the number of parts for all files", default=num_parts, type=int)

        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            response = s3.create_multipart_upload(Bucket=bucket, Key=file_name)
            upload_id = response['UploadId']

            # Calculate part size based on file size and user input
            file_size = os.path.getsize(file_path)

            # Adjust part size based on file size
            part_size = min(target_part_size, file_size)

            # Calculate the number of parts based on the adjusted part size
            num_parts = calculate_number_of_parts(file_size, part_size)

            # Use ThreadPoolExecutor for parallel uploads with increased workers
            with ThreadPoolExecutor(max_workers=10) as executor:
                args_list = [(part_number, upload_id, file_path, bucket, file_name, part_size)
                             for part_number in range(1, num_parts + 1)]

                # Upload parts in parallel
                parts = list(executor.map(lambda args: upload_part(args, bucket_region), args_list))

            # Check for errors in parts
            errors = [part for part in parts if 'Error' in part]
            if errors:
                for error in errors:
                    click.echo(f"Error uploading part {error['PartNumber']}: {error['Error']}")
                raise Exception("Upload failed.")

            s3.complete_multipart_upload(
                Bucket=bucket,
                Key=file_name,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts}
            )

            parts_total.extend(parts)
            click.echo(f"{file_name} uploaded successfully. Encryption Key: {encryption_keys[file_name]}")

        click.echo("All files in the folder uploaded successfully.")

        # Save the encryption keys at the end of the upload process
        save_encryption_keys()

        # List contents of the bucket
        try:
            s3_bucket = boto3.resource('s3').Bucket(bucket)
            objects = s3_bucket.objects.all()

            click.echo(f"Contents of bucket '{bucket}':")
            for obj in objects:
                click.echo(obj.key)

        except NoCredentialsError:
            click.echo("Credentials not available. Please set up your AWS credentials.")
        except Exception as e:
            click.echo(f"An error occurred: {str(e)}")

    except FileNotFoundError:
        click.echo(f"The folder '{folder_path}' does not exist.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please provide valid AWS access key and secret access key.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")