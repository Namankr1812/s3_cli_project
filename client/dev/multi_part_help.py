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



@cli.command()
def help():
    """Display help information for your script."""
    click.echo("--user\t\tFor accessing to create a Bucket ,Muliti-part Upload , Delete File and Listing files.")
    click.echo("--watch\t\tFor Watching the change of directory")
    click.echo("--help\t\tTo get access of all commands")
    # Add more general options if needed
    click.echo("For more information, run 'python your_script.py --help'")