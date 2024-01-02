import click
import boto3
from botocore.exceptions import NoCredentialsError, ParamValidationError
import json
session = boto3.Session()
s3 = session.resource('s3')


def enable_encryption_at_rest(bucket_name):
    try:
        s3 = session.client('s3')
        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }
                ]
            }
        )
        click.echo(f"Encryption at rest enabled for {bucket_name}.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except ParamValidationError as e:
        click.echo(f"Error enabling encryption at rest: {str(e)}")


def enable_encryption_in_transit(bucket_name):
    try:
        s3 = session.client('s3')
        bucket_policy = {
            "Version": "2012-10-17",
            "Id": "PutObjPolicy",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}/*"
                    ],
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        }
                    }
                }
            ]
        }
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        click.echo(f"Encryption in transit enabled for {bucket_name}.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except ParamValidationError as e:
        click.echo(f"Error enabling encryption in transit: {str(e)}")


def enable_encryption(bucket_name):
    click.echo(f"Enabling encryption for {bucket_name}...")
    enable_encryption_at_rest(bucket_name)
    enable_encryption_in_transit(bucket_name)


def delete_files_interactive(bucket, paths_to_delete):
    """
    Interactive way to delete files or folders from an S3 bucket.
    """
    try:
        # Print encryption status
        s3 = session.client('s3')
        encryption_at_rest = s3.get_bucket_encryption(Bucket=bucket).get('ServerSideEncryptionConfiguration', None)
        encryption_in_transit = s3.get_bucket_policy(Bucket=bucket)['Policy']

        click.echo(f"Encryption at rest: {'enabled' if encryption_at_rest else 'disabled'}")
        click.echo(f"Encryption in transit: {'enabled' if 'aws:SecureTransport' in encryption_in_transit else 'disabled'}")

        # Proceed with deletion
        deleted_files = []

        if not paths_to_delete:
            click.echo("No paths specified for deletion. Exiting.")
            return

        for path_to_delete in paths_to_delete:
            try:
                if path_to_delete.endswith('/'):
                    # If the path ends with '/', treat it as a folder
                    delete_option = click.confirm(f"Do you want to delete the folder '{path_to_delete}'?", default=False)
                    
                    if delete_option:
                        # Delete all objects inside the folder
                        objects_to_delete = s3.list_objects_v2(Bucket=bucket, Prefix=path_to_delete)
                        objects = objects_to_delete.get('Contents', [])

                        for obj in objects:
                            s3.delete_object(Bucket=bucket, Key=obj['Key'])
                            deleted_files.append(obj['Key'])
                            click.echo(f"{obj['Key']} deleted successfully.")
                        click.echo(f"Folder '{path_to_delete}' deleted successfully.")
                    else:
                        click.echo(f"Skipped deleting folder '{path_to_delete}'.")
                else:
                    # If the path doesn't end with '/', treat it as a single file
                    delete_option = click.confirm(f"Do you want to delete the file '{path_to_delete}'?", default=False)
                    
                    if delete_option:
                        s3.delete_object(Bucket=bucket, Key=path_to_delete)
                        deleted_files.append(path_to_delete)
                        click.echo(f"{path_to_delete} deleted successfully.")
                    else:
                        click.echo(f"Skipped deleting file '{path_to_delete}'.")
            except Exception as e:
                click.echo(f"An error occurred while deleting {path_to_delete}: {str(e)}")

        click.echo("Files or folders deleted successfully:")
        for deleted_item in deleted_files:
            click.echo(deleted_item)

    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")


@click.command()
@click.option('--bucket', prompt='Enter the S3 bucket name', help='Name of the S3 bucket')
@click.option('--command', prompt='Enter the command (delete_files_interactive)', help='Command to execute')
def main(bucket, command):
    """
    Main function to execute commands on an S3 bucket.
    """
    # Enable encryption at rest and in transit
    enable_encryption(bucket)

    if command == 'delete_files_interactive':
        paths_to_delete = click.prompt("Enter the file names to delete (separated by space):").split()
        delete_files_interactive(bucket, paths_to_delete)
    else:
        click.echo(f"Unsupported command: {command}")


if __name__ == '__main__':
    main()
