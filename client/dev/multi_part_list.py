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


def list_folder_contents(bucket, region="eu-north-1"):
    """
    List the contents of an S3 bucket with serial numbers.
    """
    try:
        # List contents of the bucket
        s3 = session.client('s3', region_name=region)
        response = s3.list_objects_v2(Bucket=bucket)
        contents = response.get('Contents', [])

        # Collect data for the table
        table_data = []

        # Iterate over the bucket's objects and collect information
        for index, content in enumerate(contents, start=1):
            # Add data to the table with a serial number
            table_data.append([str(index), content['Key']])

        # Display the table
        headers = ["S.No", "File Name"]
        click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")