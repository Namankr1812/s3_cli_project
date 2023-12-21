import click
import boto3
from botocore.exceptions import NoCredentialsError

session = boto3.Session()
s3 = session.resource('s3')


def delete_files_interactive(bucket, paths_to_delete):
    """
    Interactive way to delete files or folders from an S3 bucket.
    """
    try:
        s3 = session.client('s3')
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
    if command == 'delete_files_interactive':
        paths_to_delete = click.prompt("Enter the file names to delete (separated by space):").split()
        delete_files_interactive(bucket, paths_to_delete)
    else:
        click.echo(f"Unsupported command: {command}")