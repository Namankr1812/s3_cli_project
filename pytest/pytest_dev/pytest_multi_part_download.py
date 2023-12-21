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

session = boto3.Session()
s3 = session.resource('s3')



def download_file(bucket, file_name, local_directory):
    """
    Download a file from S3 to the local storage.
    """
    try:
        s3 = session.client('s3')

        # Ensure the local directory exists
        os.makedirs(local_directory, exist_ok=True)

        local_path = os.path.join(local_directory, file_name)
        s3.download_file(bucket, file_name, local_path)

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
        s3 = session.client('s3')
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