import click
import boto3
import os
import base64
import json
from botocore.exceptions import NoCredentialsError
from cryptography.fernet import Fernet
from click import prompt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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


def enable_encryption_at_rest(bucket_name):
    try:
        s3 = session.client('s3')
        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }
                ]
            }
        )
        click.echo(f"Encryption at rest enabled for {bucket_name}.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"Error enabling encryption at rest: {str(e)}")


def enable_encryption_in_transit(bucket_name):
    try:
        s3 = session.client('s3')
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy='''{
                "Version": "2012-10-17",
                "Id": "PutObjPolicy",
                "Statement": [
                    {
                        "Effect": "Deny",
                        "Principal": "*",
                        "Action": "s3:*",
                        "Resource": [
                            "arn:aws:s3:::%s/*"
                        ],
                        "Condition": {
                            "Bool": {
                                "aws:SecureTransport": "false"
                            }
                        }
                    }
                ]
            }''' % bucket_name
        )
        click.echo(f"Encryption in transit enabled for {bucket_name}.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"Error enabling encryption in transit: {str(e)}")


def get_s3_endpoint(bucket_name):
    try:
        client = boto3.client('s3')
        location = client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        return f'https://s3.{location}.amazonaws.com'
    except Exception as e:
        print(f"Error getting S3 endpoint: {e}")
        return 'https://s3.amazonaws.com'  # Default to the global S3 endpoint


def enable_encryption(bucket_name):
    click.echo(f"Enabling encryption for {bucket_name}...")
    enable_encryption_at_rest(bucket_name)
    enable_encryption_in_transit(bucket_name)


def validate_and_decode_key(encoded_key):
    try:
        # Add padding characters ('=') if needed
        encoded_key += '=' * (4 - len(encoded_key) % 4)

        # Decode the base64-encoded key
        decoded_key = base64.urlsafe_b64decode(encoded_key.encode())

        # Ensure the key is 32 bytes
        if len(decoded_key) != 32:
            raise ValueError("Invalid key length. The key must be 32 bytes.")

        return decoded_key

    except Exception as e:
        raise ValueError(f"Error validating and decoding key: {str(e)}")


def decrypt_data(data, encryption_key):
    try:
        cipher = Fernet(encryption_key)
        decrypted_data = cipher.decrypt(data)
        return decrypted_data
    except Exception as e:
        click.echo(f"Error decrypting data: {str(e)}")
        return b''  # Return an empty byte string in case of decryption failure


def download_file(bucket, file_name, local_directory, decryption_key_name):
    try:
        s3 = boto3.client('s3')

        # Ensure the local directory exists
        os.makedirs(local_directory, exist_ok=True)

        local_path = os.path.join(local_directory, file_name)

        # Download the file from S3
        s3.download_file(bucket, file_name, local_path)

        # Check if the file is encrypted (using server-side encryption)
        encryption_info = s3.head_object(Bucket=bucket, Key=file_name).get('ServerSideEncryption', None)

        if encryption_info:
            # Check if a decryption key is available
            decryption_key = encryption_keys.get(decryption_key_name)

            if decryption_key:
                try:
                    # Decrypt the downloaded file
                    with open(local_path, 'rb') as file:
                        encrypted_data = file.read()
                        decrypted_data = decrypt_data(encrypted_data, decryption_key)

                    # Write the decrypted data back to the local file
                    with open(local_path, 'wb') as file:
                        file.write(decrypted_data)

                    click.echo(f"{file_name} downloaded and decrypted to {local_path} successfully.")
                except Exception as e:
                    click.echo(f"Error decrypting data: {str(e)}")
            else:
                click.echo("Decryption key  found. File downloaded  decryption.")
        else:
            click.echo(f"{file_name} downloaded to {local_path} successfully.")

    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")


def download_from_s3(bucket):
    try:
        enable_encryption(bucket)

        s3 = session.client('s3')

        encryption_at_rest = s3.get_bucket_encryption(Bucket=bucket).get('ServerSideEncryptionConfiguration', None)
        encryption_in_transit = s3.get_bucket_policy(Bucket=bucket)['Policy']

        click.echo(f"Encryption at rest: {'enabled' if encryption_at_rest else 'disabled'}")
        click.echo(f"Encryption in transit: {'enabled' if 'aws:SecureTransport' in encryption_in_transit else 'disabled'}")

        bucket_contents = s3.list_objects_v2(Bucket=bucket).get('Contents', [])

        if not bucket_contents:
            click.echo(f"No files in the bucket '{bucket}'.")
            return

        click.echo(f"Files in the bucket '{bucket}':")
        for content in bucket_contents:
            click.echo(content['Key'])

        file_to_download = click.prompt("Enter the file name to download")
        local_directory = click.prompt("Enter the local directory to save the file")
        decryption_key_name = click.prompt("Enter the name of the encryption key: ")

        download_file(bucket, file_to_download, local_directory, decryption_key_name)

    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")



