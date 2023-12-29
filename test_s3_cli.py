import os
import tempfile
import shutil
import pytest
import click
import boto3
import time
import unittest
import tabulate
from unittest.mock import patch, Mock
from concurrent.futures import ThreadPoolExecutor, as_completed
from test_s3_cli_folder import create_folder, upload_folder, list_folder_contents, delete_files_interactive
from click.testing import CliRunner
from test_s3_cli_folder import executor
from tabulate import tabulate
import botocore

s3_client = boto3.client('s3')

@click.group()
def upload_command():
    pass

class CaptureCalls:
    def __init__(self, obj, method_name):
        self.obj = obj
        self.method_name = method_name
        self.calls = []

    def __enter__(self):
        self.original_method = getattr(self.obj, self.method_name)
        setattr(self.obj, self.method_name, self._capturing_method)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        setattr(self.obj, self.method_name, self.original_method)

    def _capturing_method(self, *args, **kwargs):
        call_info = {'args': args, 'kwargs': kwargs}
        self.calls.append(call_info)
        return self.original_method(*args, **kwargs)

def does_folder_exist_in_bucket(s3_client, folder_path, bucket_name):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    return 'Contents' in response

@pytest.fixture
def temp_folder():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    try:
        shutil.rmtree(temp_dir)
        print(f"Deleted temporary folder: {temp_dir}")
    except Exception as e:
        print(f"Error deleting temporary folder {temp_dir}: {e}")

def test_create_folder():
    folder_name = "note1_folder1"
    user_bucket = "irisbucket"
    s3_folder_path = f"{folder_name}-{user_bucket}/"

    assert not does_folder_exist_in_bucket(s3_client, s3_folder_path, user_bucket), f"Folder already exists in bucket: {s3_folder_path}"
    assert create_folder(s3_client, folder_name, user_bucket) is True
    time.sleep(1)
    assert does_folder_exist_in_bucket(s3_client, s3_folder_path, user_bucket), f"Folder does not exist in bucket: {s3_folder_path}"

@upload_command.command()
@click.argument('folder')
@click.argument('bucket')
@click.option('--target-part-size', default=5242880, help='Target size of each part in bytes')
@click.option('--num-parts', default=5, help='Number of parts to split the file into')
def upload(folder, bucket, target_part_size, num_parts):
    # Function logic goes here
    pass

# Remove the upload_folder command from the click.group decorator
# upload_command.add_command(upload_folder)

@pytest.fixture
def mock_s3_resource(monkeypatch):
    # Mock the S3 resource to avoid actual S3 operations during testing
    class MockS3Resource:
        def Bucket(self, _):
            return MockBucket()

    class MockBucket:
        def objects(self):
            return []

    monkeypatch.setattr(boto3, "resource", lambda *args, **kwargs: MockS3Resource())

@pytest.fixture
def temp_folder():
    # Create a temporary folder for testing
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up the temporary folder after the test
    shutil.rmtree(temp_dir)

@unittest.mock.patch('boto3.resource')
def test_upload_folder(mock_s3_resource):
    # Mock S3 resource
    mock_bucket = unittest.mock.Mock()
    mock_bucket.objects.all.return_value = [
        unittest.mock.Mock(key=f"test_file_{i}.txt") for i in range(3)
    ]
    mock_s3_resource.return_value.Bucket.return_value = mock_bucket

    temp_folder = r'C:\Users\naman-axcess\Desktop\multipart_upload\AWS File'

    # Generate dummy file paths
    dummy_file_paths = []
    for i in range(3):
        dummy_file_path = os.path.join(temp_folder, f"test_file_{i}.txt")
        with open(dummy_file_path, "w") as f:
            f.write(f"Test content for file {i}")
        dummy_file_paths.append(dummy_file_path)

    try:
        # Directly invoke the upload_folder function for testing
        upload_folder(temp_folder, "test_bucket", target_part_size=5242880, num_parts=5)

        # Assert that the bucket is empty initially
        s3_bucket = mock_s3_resource.return_value.Bucket.return_value
        assert len(list(s3_bucket.objects.all())) == 3

        # Assert that the expected files are present in the bucket after the upload
        expected_keys = [os.path.basename(file_path) for file_path in dummy_file_paths]
        actual_keys = [obj.key for obj in s3_bucket.objects.all()]
        assert set(expected_keys) == set(actual_keys)

    finally:
        # Cleanup: Remove the dummy files after the test
        for file_path in dummy_file_paths:
            os.remove(file_path)

@click.command(name='delete-files-interactive')
def delete_files_interactive(bucket, file_path):
    user_bucket = "irisbucket"
    s3_file_path = "test_file.txt"
    s3_test_path = f"{s3_file_path}-{user_bucket}/"
    os.makedirs(os.path.join(temp_folder, s3_test_path))

    runner = CliRunner()
    result = runner.invoke(delete_files_interactive, [user_bucket, s3_file_path])

    assert result.exit_code == 0
    assert f"Deleted file {s3_file_path}" in result.output

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

def print_test_summary():
    # Read the HTML report file
    with open("report.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")

    # Extract the test results
    test_results = []
    for index, row in enumerate(soup.select("#results-table tbody tr"), start=1):
        cells = [index] + [cell.text.strip() for cell in row.select("td")]
        test_results.append(cells)

    # Display the test results in a tabular format
    headers = ["Serial No", "Test Name", "Status", "Duration"]
    print(tabulate(test_results, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    # Run pytest and print the test summary
    result_code = pytest.main(["-qq", "--html=report.html", "--self-contained-html"])

    # Print the test summary
    print_test_summary()

    # Exit with the pytest result code
    exit(result_code)
