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

session = boto3.Session()
s3 = session.resource('s3')

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
    cipher = Fernet(encryption_key)
    encrypted_data = cipher.encrypt(data)
    return encrypted_data

def decrypt_data(data, encryption_key):
    cipher = Fernet(encryption_key)
    decrypted_data = cipher.decrypt(data)
    return decrypted_data

def upload_part(args, encryption_key=None, bucket_region='us-east-1'):
    part_number, upload_id, file_path, bucket, file_name, part_size = args
    s3_endpoint = get_s3_endpoint(bucket)

    with open(file_path, 'rb') as file:
        file.seek(part_size * (part_number - 1))
        data = file.read(part_size)

        # Check if client-side encryption is enabled
        if encryption_key:
            data = encrypt_data(data, encryption_key)

        # Specify the server-side encryption algorithm
        s3 = boto3.client('s3', endpoint_url=s3_endpoint, region_name=bucket_region)
        sse_algorithm = 'AES256'  # Use 'AES256' for Amazon S3 managed keys

        # Assuming encryption_key is the client-side encryption key
        sse_customer_key = encryption_key.encode('utf-8').hex() if encryption_key else None

        # Use SSECustomerKey only if it's not None
        s3_upload_args = {
            'Bucket': bucket,
            'Key': file_name,
            'UploadId': upload_id,
            'PartNumber': part_number,
        }
        headers = {
            'x-amz-server-side-encryption-customer-algorithm': sse_algorithm,
            'x-amz-server-side-encryption-customer-key': sse_customer_key,
        }
        if sse_customer_key:
            s3_upload_args['Headers'] = headers

        try:
            response = s3.upload_part(Body=data, **s3_upload_args)
        except Exception as e:
            click.echo(f"An error occurred: {str(e)}")
            return  # Exit the function if an error occurs

    etag = response["ETag"]
    return {"PartNumber": part_number, "ETag": etag}



@click.option("--target-part-size", default=None, type=int, help="Size of each part in bytes")
@click.option("--num-parts", default=None, type=int, help="Number of parts for each file")
@click.option("--encryption-key", default=None, help="Encryption key for client-side encryption/decryption")
# ...

def upload_folder(folder_path, bucket, target_part_size=None, num_parts=None, encryption_key=None):
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
                parts = list(executor.map(lambda args: upload_part(args, encryption_key, bucket_region), args_list))

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
            click.echo(f"{file_name} uploaded successfully.")

        click.echo("All files in the folder uploaded successfully.")

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


