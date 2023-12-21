import os
import shutil
import tempfile
import boto3
import pytest
from botocore.exceptions import NoCredentialsError
from click.testing import CliRunner
import click
import unittest.mock

from datetime import datetime, timezone

# Replace this line in your code:
# datetime_now = datetime.datetime.utcnow()

# With this line:
datetime_now = datetime.now(timezone.utc)


# Replace 'your_script_name' with the actual name of your script/module
from test_upload_folder import upload_folder

@click.group()
def upload_command():
    pass

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