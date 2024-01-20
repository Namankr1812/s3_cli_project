import os
import json
import base64
from cryptography.fernet import Fernet
from unittest.mock import patch
import pytest

from test_upload_folder import upload_folder, encryption_keys, save_encryption_keys

@pytest.fixture
def mock_boto3():
    with patch('test_upload_folder.boto3') as mock_boto3:
        yield mock_boto3

def generate_encryption_key():
    key = os.urandom(32)
    return key

def test_upload_folder(mock_boto3, tmpdir):
    # Set up temporary folder with test files
    temp_folder = str(tmpdir)
    file1_path = os.path.join(temp_folder, 'test_file1.txt')
    file2_path = os.path.join(temp_folder, 'test_file2.txt')

    with open(file1_path, 'w') as file1:
        file1.write("Test content for file 1")

    with open(file2_path, 'w') as file2:
        file2.write("Test content for file 2")

    # Mock S3 resource
    mock_bucket = mock_boto3.resource.return_value.Bucket.return_value
    mock_bucket.meta.client.meta.region_name = 'us-east-1'

    # Mock the response of create_multipart_upload
    mock_boto3.client.return_value.create_multipart_upload.return_value = {'UploadId': 'mock_upload_id'}

    # Generate and save a test encryption key
    test_key = generate_encryption_key()
    encryption_keys = {os.path.basename(file1_path): test_key.decode('latin1')}
    with open('encryption_keys.json', 'w') as file:
        json.dump(encryption_keys, file)

    # Call the upload_folder function
    with patch('test_upload_folder.upload_part', return_value={"PartNumber": 1, "ETag": "mock_etag_1"}):
        upload_folder(temp_folder, "test_bucket", target_part_size=5242880, num_parts=5)

    # Assert that encryption keys are stored and match expected
    saved_encryption_keys = json.load(open('encryption_keys.json', 'r'))
    for file_path, key in encryption_keys.items():
        assert file_path in saved_encryption_keys
        assert saved_encryption_keys[file_path] == key

    # Cleanup: Remove the 'encryption_keys.json' file after the test
    os.remove('encryption_keys.json')

# Uncomment the line below if you want to run the tests
# pytest -v test_your_module.py
