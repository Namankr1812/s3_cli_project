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


def delete_files(bucket, paths_to_delete):
    """
    Delete files or folders from an S3 bucket.
    """
    try:
        # Delete files or folders from the bucket
        s3 = session.client('s3')
        deleted_files = []

        for path_to_delete in paths_to_delete:
            try:
                if path_to_delete.endswith('/'):
                    # If the path ends with '/', treat it as a folder and delete all objects inside
                    objects_to_delete = s3.list_objects_v2(Bucket=bucket, Prefix=path_to_delete)
                    objects = objects_to_delete.get('Contents', [])

                    for obj in objects:
                        s3.delete_object(Bucket=bucket, Key=obj['Key'])
                        deleted_files.append(obj['Key'])
                        click.echo(f"{obj['Key']} deleted successfully.")
                else:
                    # If the path doesn't end with '/', treat it as a single file and delete it
                    s3.delete_object(Bucket=bucket, Key=path_to_delete)
                    deleted_files.append(path_to_delete)
                    click.echo(f"{path_to_delete} deleted successfully.")
            except Exception as e:
                click.echo(f"An error occurred while deleting {path_to_delete}: {str(e)}")

        click.echo("Files or folders deleted successfully:")
        for deleted_item in deleted_files:
            click.echo(deleted_item)

    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")