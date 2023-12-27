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

def view_s3_bucket_logs(bucket_name):
    try:
        # Create an S3 resource using the provided bucket name
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)

        # Collect data for the table
        table_data = []

        # Iterate over the bucket's objects and collect information
        for index, obj in enumerate(bucket.objects.all(), start=1):
            size_mb = obj.size / (1024 ** 2)  # Convert size to megabytes
            timing = obj.last_modified.strftime("%Y-%m-%d %H:%M:%S")  # Format timing as a string

            # Add data to the table with a smaller serial number
            table_data.append([str(index), obj.key, f"{size_mb:.2f} MB", timing])

        # Display the table
        headers = ["S.No", "Name", "Size", "Timing of Uploading"]
        click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

        click.echo(f"S3 bucket activity logs for '{bucket_name}':")
    except Exception as e:
        click.echo(f"Error retrieving S3 bucket activity logs: {str(e)}")