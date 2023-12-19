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


@click.group()
def cli():
    pass

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
file_path = r"C:\Users\naman-axcess\Desktop\multipart upload\s3_cli.py"

try:
    hash_value = calculate_file_hash(file_path)
    print(f"SHA-256 hash of {file_path}: {hash_value}")
except Exception as e:
    print(f"Error calculating hash: {e}")