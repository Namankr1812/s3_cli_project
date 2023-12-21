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



import uuid

def create_folder(folder_name, user_bucket, region="eu-north-1"):
    """
    Create a new folder (object key prefix) within the user-specified bucket.
    """
    try:
        unique_id = str(uuid.uuid4())[:8]
        unique_folder_name = f"{folder_name}-{unique_id}/"  # Add a trailing slash for visual hierarchy

        s3 = session.client('s3', region_name=region)
        s3.put_object(Bucket=user_bucket, Key=unique_folder_name)

        click.echo(f"Folder {unique_folder_name} created successfully within '{user_bucket}'.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")
        logging.error(f"Error creating folder: {str(e)}")