import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from botocore.exceptions import NoCredentialsError
from test_newcreation_folder import create_folder

class TestCreateFolderFunction(unittest.TestCase):



    @patch('builtins.input', side_effect=['test_bucket', 'test_folder'])
    @patch('test_newcreation_folder.session.client', side_effect=NoCredentialsError())
    def test_create_folder_no_credentials(self, mock_client, mock_input):
        # Redirect stdout to capture the output
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Call the function
            create_folder(folder_name='test_folder', user_bucket='test_bucket', region='eu-north-1')

        # Assert the output
        expected_output = "Credentials not available. Please set up your AWS credentials.\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('builtins.input', side_effect=['test_bucket', 'test_folder'])
    @patch('test_newcreation_folder.session.client', side_effect=NoCredentialsError())
    def test_create_folder_no_credentials(self, mock_client, mock_input):
        # Redirect stdout to capture the output
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Call the function
            create_folder(folder_name='new_folder', user_bucket='new_bucket', region='eu-north-1')

        # Assert the output
        expected_output = "Credentials not available. Please set up your AWS credentials.\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)

if __name__ == '__main__':
    unittest.main()
