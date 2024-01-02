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

def calculate_file_hash(file_path, block_size=65536):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for block in iter(lambda: file.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

# Example usage:
file_path = r"D:\multipart_upload\client\client.py"

try:
    hash_value = calculate_file_hash(file_path)
    print(f"SHA-256 hash of {file_path}: {hash_value}")
except Exception as e:
    print(f"Error calculating hash: {e}")
