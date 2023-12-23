import pytest
from click.testing import CliRunner
from unittest.mock import patch
from botocore.exceptions import NoCredentialsError
from test_download_folder import download_file  # Replace 'your_module' with the actual name of your module
import traceback
import logging

# ... Other imports and fixtures ...

def test_download_file_no_credentials(tmp_path, mocker, caplog):
    mocker.patch('test_download_folder.boto3.Session.client', side_effect=NoCredentialsError)

    bucket = "irisbucket"
    file_name = "cam7.mp4"
    local_directory = str(tmp_path)

    # Invoke the download_file function
    try:
        # Patching root logger to capture logs
        with caplog.at_level(logging.ERROR):
            result = CliRunner().invoke(download_file, [bucket, file_name, local_directory], prog_name='your_program_name')
    except NoCredentialsError as e:
        # Check if NoCredentialsError was raised
        assert 'NoCredentialsError' in str(e)
    except Exception as e:
        # Print out the exception and its traceback
        print("Exception:", repr(e))
        traceback.print_exc()

    # Print out the captured log messages
    print("Captured Log Messages:", caplog.text)

    # Your assertions for the test go here
    assert result.exit_code != 0
