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

from dev import multi_part_upload
from dev import multi_part_delete
from dev import multi_part_download
from dev import multi_part_list
from dev import multi_part_hash
from dev import multi_part_logs
from dev import multi_part_new_folder_creation

session = boto3.Session()

@click.group()
def cli():
    pass

#------------------------------------------------------------user------------------------------------------------------------

# Assuming you have a session and s3 resource object defined
session = boto3.Session()
s3 = session.resource('s3')

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize the bucket variable
bucket = None

def create_bucket():
    try:
        # Prompt the user for the bucket name and region
        bucket_name = click.prompt("Enter the S3 bucket name")
        region = click.prompt("Enter the region for the bucket (e.g., us-east-1)")

        s3 = session.client('s3', region_name=region)
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})

        click.echo(f"Bucket {bucket_name} created successfully.")
        return bucket_name
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
        return None
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")
        logging.error(f"Error creating bucket: {str(e)}")
        return None

def list_buckets():
    try:
        # List existing buckets
        s3 = session.client('s3')
        response = s3.list_buckets()
        return [bucket['Name'] for bucket in response.get('Buckets', [])]
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
        return []
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")
        return []

@cli.command()
def user():
    global bucket

    click.echo("Welcome to the S3 CLI!")

    # Prompt the user to set up an ID and password
    user_id = click.prompt("Enter your user ID")
    password = click.prompt("Enter your password", hide_input=True, confirmation_prompt=True)

    click.echo(f"User ID: {user_id} set up successfully.")

    # Prompt the user to create a new bucket or use an existing one
    create_new_bucket = click.confirm("Do you want to create a new bucket?", default=True)

    if create_new_bucket:
        # Create a new bucket
        bucket = create_bucket()
        if not bucket:
            return
    else:
        # Use an existing bucket
        existing_buckets = list_buckets()
        if not existing_buckets:
            click.echo("No existing buckets found.")
            return

        click.echo("Existing buckets:")
        for index, existing_bucket in enumerate(existing_buckets, start=1):
            click.echo(f"{index}. {existing_bucket}")

        selected_bucket_index = click.prompt("Choose a bucket (enter the number)", type=int, show_default=True, default=1)
        if 1 <= selected_bucket_index <= len(existing_buckets):
            bucket = existing_buckets[selected_bucket_index - 1]
        else:
            click.echo("Invalid selection. Using the first bucket.")
            bucket = existing_buckets[0]

    while True:
        click.echo("\nWhat would you like to do?")
        click.echo("1. Create a new folder in S3")
        click.echo("2. Upload and list files in S3")
        click.echo("3. List the contents of a folder in S3")
        click.echo("4. Delete files in S3")
        click.echo("5. Download a file from S3")
        click.echo("6. View S3 bucket activity logs")
        click.echo("7. Switch S3 Bucket")
        click.echo("8. Exit")

        choice = click.prompt("Enter your choice")

        if choice == "1":
            folder_name = click.prompt("Enter the folder name")
            multi_part_new_folder_creation.create_folder(folder_name, bucket)
            logging.info(f"Created folder: {folder_name}")
        elif choice == "2":
            folder_path = click.prompt("Enter the folder path")
            multi_part_upload.upload_folder(folder_path, bucket)
            logging.info(f"Uploaded files from {folder_path} to S3 bucket {bucket}")
        elif choice == "3":
            multi_part_list.list_folder_contents(bucket)
            logging.info(f"Listed contents of S3 bucket {bucket}")
        elif choice == "4":
            files_to_delete = click.prompt("Enter the file names to delete (separated by space)").split()
            multi_part_delete.delete_files_interactive(bucket, files_to_delete)
            logging.info(f"Deleted files {files_to_delete} from S3 bucket {bucket}")
        elif choice == "5":
            multi_part_download.download_from_s3(bucket)
            logging.info(f"Downloaded a file from S3 bucket {bucket}")
        elif choice == "6":
            multi_part_logs.view_s3_bucket_logs(bucket)
        elif choice == "7":
            # Allow the user to switch to a different bucket
            existing_buckets = list_buckets()
            if not existing_buckets:
                click.echo("No existing buckets found.")
                continue

            click.echo("Existing buckets:")
            for index, existing_bucket in enumerate(existing_buckets, start=1):
                click.echo(f"{index}. {existing_bucket}")

            selected_bucket_index = click.prompt("Choose a bucket (enter the number)", type=int, show_default=True, default=1)
            if 1 <= selected_bucket_index <= len(existing_buckets):
                bucket = existing_buckets[selected_bucket_index - 1]
                click.echo(f"Switched to bucket: {bucket}")
            else:
                click.echo("Invalid selection. Using the current bucket.")
        elif choice == "8":
            break
        else:
            click.echo("Invalid choice. Please try again.")


def get_file_state(directory, recursive):
    file_state = set()
    for root, dirs, files in os.walk(directory):
        if not recursive and root != directory:
            break
        for file in files:
            file_state.add(os.path.relpath(os.path.join(root, file), directory))
    return file_state

@cli.command()
@click.option("--interval", default=1, help="Interval in seconds to check for file changes")
@click.option("--recursive/--no-recursive", default=False, help="Watch directory recursively")
@click.argument("directory", type=click.Path(exists=True))
def watch(interval, recursive, directory):
    click.echo(f"Watching directory: {directory}")
    click.echo("Press Ctrl+C to stop...")

    initial_state = get_file_state(directory, recursive)
    start_times = {}

    try:
        while True:
            current_state = get_file_state(directory, recursive)

            added_files = current_state - initial_state
            removed_files = initial_state - current_state
            modified_files = set()

            for file in initial_state & current_state:
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    modified_time = os.path.getmtime(file_path)
                    if modified_time > start_times.get(file, 0):
                        modified_files.add(file)
                        start_times[file] = modified_time

            if added_files:
                click.echo("Added files:")
                for file in added_files:
                    click.echo(f"- {file}")

            if removed_files:
                click.echo("REMOVED Files:")
                for file in removed_files:
                    click.echo(f"- {file}")

            if modified_files:
                click.echo("Modified files:")
                for file in modified_files:
                    click.echo(f"- {file}")

            initial_state = current_state
            time.sleep(interval)

    except KeyboardInterrupt:
        click.echo("Watch command stopped")

#----------------------------------------------------HELP COMMANDS---------------------------------------------------------

@cli.command()
def help():
    """Display help information for your script."""
    click.echo("--user\t\tFor accessing to create a Bucket ,Muliti-part Upload , Delete File and Listing files.")
    click.echo("--watch\t\tFor Watching the change of directory")
    click.echo("--help\t\tTo get access of all commands")
    # Add more general options if needed
    click.echo("For more information, run 'python your_script.py --help'")


def calculate_file_hash(file_path, block_size=65536):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for block in iter(lambda: file.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

# Example usage:
file_path = r"C:\Users\naman-axcess\Desktop\multipart_upload\client\client.py"

try:
    hash_value = calculate_file_hash(file_path)
    print(f"SHA-256 hash of {file_path}: {hash_value}")
except Exception as e:
    print(f"Error calculating hash: {e}")

if __name__ == '__main__':
    cli()