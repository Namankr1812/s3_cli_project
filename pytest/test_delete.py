import unittest.mock
import sys
import io
from click.testing import CliRunner
from test_delete_folder import delete_files_interactive, main

def test_delete_files_interactive():
    bucket_name = "irisbucket"
    paths_to_delete = ["cam5.mp4", "cam3.mp4"]

    # Use CliRunner to simulate interactive input
    runner = CliRunner()

    # Mock the click.confirm function to simulate user input
    with unittest.mock.patch('click.confirm', return_value=True):
        # Mock the S3 client and list_objects_v2 method
        with unittest.mock.patch('boto3.client') as mock_boto_client:
            mock_s3_client = mock_boto_client.return_value
            mock_s3_client.list_objects_v2.return_value = {
                'Contents': [{'Key': 'cam5.mp4'}, {'Key': 'cam3.mp4'}]
            }

            # Mock the delete_object method
            with unittest.mock.patch.object(mock_s3_client, 'delete_object'):
                # Run the delete_files_interactive function
                delete_files_interactive(bucket_name, paths_to_delete)



