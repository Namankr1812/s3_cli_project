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

from botocore.exceptions import NoCredentialsError
from concurrent.futures import ThreadPoolExecutor, as_completed
from click import prompt
from tabulate import tabulate
from boto3.s3.transfer import TransferConfig
from cryptography.fernet import Fernet
session = boto3.Session()
s3 = session.resource('s3')

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

def enable_encryption(bucket_name):
    click.echo(f"Enabling encryption for {bucket_name}...")
    enable_encryption_at_rest(bucket_name)
    enable_encryption_in_transit(bucket_name)



def decrypt_data(data, decryption_key):
    cipher = Fernet(decryption_key)
    decrypted_data = cipher.decrypt(data)
    return decrypted_data

def download_file(bucket, file_name, local_directory, decryption_key=None):
    """
    Download a file from S3 to the local storage.
    """
    try:
        s3 = session.client('s3')

        # Ensure the local directory exists
        os.makedirs(local_directory, exist_ok=True)

        local_path = os.path.join(local_directory, file_name)

        # Download the file from S3
        s3.download_file(bucket, file_name, local_path)

        # Check if the file is encrypted (using server-side encryption)
        encryption_info = s3.head_object(Bucket=bucket, Key=file_name).get('ServerSideEncryption', None)

        if encryption_info and decryption_key:
            # Decrypt the downloaded file
            with open(local_path, 'rb') as file:
                encrypted_data = file.read()
                decrypted_data = decrypt_data(encrypted_data, decryption_key)

            # Write the decrypted data back to the local file
            with open(local_path, 'wb') as file:
                file.write(decrypted_data)

        click.echo(f"{file_name} downloaded to {local_path} successfully.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")



def download_from_s3(bucket):
    """
    Download files from S3 to the local storage.
    """
    try:
        enable_encryption(bucket)

        s3 = session.client('s3')

        # Print encryption status
        encryption_at_rest = s3.get_bucket_encryption(Bucket=bucket).get('ServerSideEncryptionConfiguration', None)
        encryption_in_transit = s3.get_bucket_policy(Bucket=bucket)['Policy']

        click.echo(f"Encryption at rest: {'enabled' if encryption_at_rest else 'disabled'}")
        click.echo(f"Encryption in transit: {'enabled' if 'aws:SecureTransport' in encryption_in_transit else 'disabled'}")

        # Continue with the download
        bucket_contents = s3.list_objects_v2(Bucket=bucket).get('Contents', [])

        if not bucket_contents:
            click.echo(f"No files in the bucket '{bucket}'.")
            return

        click.echo(f"Files in the bucket '{bucket}':")
        for content in bucket_contents:
            click.echo(content['Key'])

        file_to_download = click.prompt("Enter the file name to download")
        local_directory = click.prompt("Enter the local directory to save the file")

        download_file(bucket, file_to_download, local_directory)

    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")
