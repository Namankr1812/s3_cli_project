import click
import boto3
import os
import time
import math
import datetime
import uuid
import logging


from botocore.exceptions import NoCredentialsError
from concurrent.futures import ThreadPoolExecutor, as_completed
from click import prompt
from tabulate import tabulate



session = boto3.Session()

@click.group()
def cli():
    pass

#------------------------------------------------------------user------------------------------------------------------------

# Assuming you have a session and s3 resource object defined
session = boto3.Session()
s3 = session.resource('s3')

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize the bucket variable
bucket = None

def create_bucket():
    try:
        # Prompt the user for the bucket name and region
        bucket_name = click.prompt("Enter the S3 bucket name")
        region = click.prompt("Enter the region for the bucket (e.g., us-east-1)")

        s3 = session.client('s3', region_name=region)
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})

        click.echo(f"Bucket {bucket_name} created successfully.")
        return bucket_name
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
        return None
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")
        logging.error(f"Error creating bucket: {str(e)}")
        return None

def list_buckets():
    try:
        # List existing buckets
        s3 = session.client('s3')
        response = s3.list_buckets()
        return [bucket['Name'] for bucket in response.get('Buckets', [])]
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
        return []
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")
        return []

@cli.command()
def user():
    global bucket

    click.echo("Welcome to the S3 CLI!")

    # Prompt the user to set up an ID and password
    user_id = click.prompt("Enter your user ID")
    password = click.prompt("Enter your password", hide_input=True, confirmation_prompt=True)

    click.echo(f"User ID: {user_id} set up successfully.")

    # Prompt the user to create a new bucket or use an existing one
    create_new_bucket = click.confirm("Do you want to create a new bucket?", default=True)

    if create_new_bucket:
        # Create a new bucket
        bucket = create_bucket()
        if not bucket:
            return
    else:
        # Use an existing bucket
        existing_buckets = list_buckets()
        if not existing_buckets:
            click.echo("No existing buckets found.")
            return

        click.echo("Existing buckets:")
        for index, existing_bucket in enumerate(existing_buckets, start=1):
            click.echo(f"{index}. {existing_bucket}")

        selected_bucket_index = click.prompt("Choose a bucket (enter the number)", type=int, show_default=True, default=1)
        if 1 <= selected_bucket_index <= len(existing_buckets):
            bucket = existing_buckets[selected_bucket_index - 1]
        else:
            click.echo("Invalid selection. Using the first bucket.")
            bucket = existing_buckets[0]

    while True:
        click.echo("\nWhat would you like to do?")
        click.echo("1. Create a new folder in S3")
        click.echo("2. Upload and list files in S3")
        click.echo("3. List the contents of a folder in S3")
        click.echo("4. Delete files in S3")
        click.echo("5. Download a file from S3")
        click.echo("6. View S3 bucket activity logs")
        click.echo("7. Exit")

        choice = click.prompt("Enter your choice")

        if choice == "1":
            folder_name = click.prompt("Enter the folder name")
            create_folder(folder_name, bucket)
            logging.info(f"Created folder: {folder_name}")
        elif choice == "2":
            folder_path = click.prompt("Enter the folder path")
            upload_folder(folder_path, bucket)
            logging.info(f"Uploaded files from {folder_path} to S3 bucket {bucket}")
        elif choice == "3":
            list_folder_contents(bucket)
            logging.info(f"Listed contents of S3 bucket {bucket}")
        elif choice == "4":
            files_to_delete = click.prompt("Enter the file names to delete (separated by space)").split()
            delete_files(bucket, files_to_delete)
            logging.info(f"Deleted files {files_to_delete} from S3 bucket {bucket}")
        elif choice == "5":
            download_from_s3(bucket)
            logging.info(f"Downloaded a file from S3 bucket {bucket}")
        elif choice == "6":
            view_s3_bucket_logs(bucket)
        elif choice == "7":
            break
        else:
            click.echo("Invalid choice. Please try again.")

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


import uuid

def create_folder(folder_name, user_bucket, region="eu-north-1"):
    """
    Create a new folder (object key prefix) within the user-specified bucket.
    """
    try:
        unique_id = str(uuid.uuid4())[:8]
        unique_folder_name = f"{folder_name}-{unique_id}/"  # Add a trailing slash for visual hierarchy

        s3 = session.client('s3', region_name=region)
        s3.put_object(Bucket=user_bucket, Key=unique_folder_name)

        click.echo(f"Folder {unique_folder_name} created successfully within '{user_bucket}'.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")
        logging.error(f"Error creating folder: {str(e)}")



# Assuming you have the necessary imports and session setup here...

def calculate_number_of_parts(file_size, part_size):
    """
    Calculate the number of parts needed for a multipart upload.
    """
    return (file_size + part_size - 1) // part_size

def upload_part(args):
    """
    Upload a part of the file to S3.
    """
    part_number, upload_id, file_path, bucket, file_name, part_size = args
    s3 = session.client('s3')

    with open(file_path, 'rb') as file:
        file.seek(part_size * (part_number - 1))
        data = file.read(part_size)

        response = s3.upload_part(
            Body=data,
            Bucket=bucket,
            Key=file_name,
            UploadId=upload_id,
            PartNumber=part_number
        )

        etag = response["ETag"]
        return {"PartNumber": part_number, "ETag": etag}

def upload_folder(folder_path, bucket, target_part_size=None):
    """
    Upload files from a folder to S3 with parallel processing.
    """
    try:
        # Upload files in the folder
        s3 = session.client('s3')
        parts_total = []

        # Get a list of all files in the folder
        file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if
                      os.path.isfile(os.path.join(folder_path, file))]

        # Prompt the user for the number of parts only once
        if target_part_size is None:
            total_file_size = sum(os.path.getsize(file) for file in file_paths)

            # Calculate the default part size based on file size
            if total_file_size > 100 * 1024 * 1024:  # Large file
                target_part_size = 100 * 1024 * 1024  # Set a maximum part size for large files
            else:  # Small file
                target_part_size = 5 * 1024 * 1024  # Set a default part size for small files

            default_num_parts = calculate_number_of_parts(total_file_size, target_part_size)

            # Prompt the user for part size
            target_part_size = click.prompt("Enter part size (in bytes)", default=target_part_size, type=int)

            # Check if the user exceeds the maximum part size
            if target_part_size > 100 * 1024 * 1024:
                click.echo(f"Warning: Part size cannot exceed 100 MB. Using the default part size.")
                target_part_size = 100 * 1024 * 1024

            # Check if the user enters a custom part size less than the minimum allowed
            min_part_size = 5 * 1024 * 1024  # Minimum allowed part size
            if target_part_size < min_part_size:
                click.echo(f"Warning: Part size cannot be less than 5 MB. Using the minimum part size.")
                target_part_size = min_part_size

            # Calculate the number of parts based on the user's input
            num_parts_prompt = click.prompt(f"Enter the number of parts for all files (default is {default_num_parts})", default=default_num_parts, type=int, show_default=default_num_parts)

        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            response = s3.create_multipart_upload(Bucket=bucket, Key=file_name)
            upload_id = response['UploadId']

            # Adjust part size based on file size
            file_size = os.path.getsize(file_path)
            part_size = target_part_size
            num_parts = min(5, file_size // part_size + 1)

            # Use ThreadPoolExecutor for parallel uploads
            with ThreadPoolExecutor(max_workers=5) as executor:
                args_list = [(part_number, upload_id, file_path, bucket, file_name, part_size)
                             for part_number in range(1, num_parts + 1)]

                # Upload parts in parallel
                parts = list(executor.map(upload_part, args_list))

            # Check for errors in parts
            errors = [part for part in parts if 'Error' in part]
            if errors:
                for error in errors:
                    click.echo(f"Error uploading part {error['PartNumber']}: {error['Error']}")
                raise Exception("Upload failed.")

            s3.complete_multipart_upload(
                Bucket=bucket,
                Key=file_name,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts}
            )

            parts_total.extend(parts)
            click.echo(f"{file_name} uploaded successfully.")

        click.echo("All files in the folder uploaded successfully.")

        # List contents of the bucket
        try:
            s3_bucket = session.resource('s3').Bucket(bucket)
            objects = s3_bucket.objects.all()

            click.echo(f"Contents of bucket '{bucket}':")
            for obj in objects:
                click.echo(obj.key)

        except NoCredentialsError:
            click.echo("Credentials not available. Please set up your AWS credentials.")
        except Exception as e:
            click.echo(f"An error occurred: {str(e)}")

    except FileNotFoundError:
        click.echo(f"The folder '{folder_path}' does not exist.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please provide valid AWS access key and secret access key.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")

def delete_files(bucket, files_to_delete):
    """
    Delete files from an S3 bucket.
    """
    try:
        # Delete files from the bucket
        s3 = session.client('s3')
        deleted_files = []

        for file_name in files_to_delete:
            try:
                s3.delete_object(Bucket=bucket, Key=file_name)
                deleted_files.append(file_name)
                click.echo(f"{file_name} deleted successfully.")
            except Exception as e:
                click.echo(f"An error occurred while deleting {file_name}: {str(e)}")

        click.echo("Files deleted successfully:")
        for deleted_file in deleted_files:
            click.echo(deleted_file)

    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")

def list_folder_contents(bucket, region="eu-north-1"):
    """
    List the contents of an S3 bucket with serial numbers.
    """
    try:
        # List contents of the bucket
        s3 = session.client('s3', region_name=region)
        response = s3.list_objects_v2(Bucket=bucket)
        contents = response.get('Contents', [])

        # Collect data for the table
        table_data = []

        # Iterate over the bucket's objects and collect information
        for index, content in enumerate(contents, start=1):
            # Add data to the table with a serial number
            table_data.append([str(index), content['Key']])

        # Display the table
        headers = ["S.No", "File Name"]
        click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")

def download_file(bucket, file_name, local_directory):
    """
    Download a file from S3 to the local storage.
    """
    try:
        s3 = session.client('s3')

        # Ensure the local directory exists
        os.makedirs(local_directory, exist_ok=True)

        local_path = os.path.join(local_directory, file_name)
        s3.download_file(bucket, file_name, local_path)

        click.echo(f"{file_name} downloaded to {local_path} successfully.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")

def download_from_s3(bucket):
    """
    Download files from S3 to the local storage.
    """
    try:
        s3 = session.client('s3')
        bucket_contents = s3.list_objects_v2(Bucket=bucket).get('Contents', [])

        if not bucket_contents:
            click.echo(f"No files in the bucket '{bucket}'.")
            return

        click.echo(f"Files in the bucket '{bucket}':")
        for content in bucket_contents:
            click.echo(content['Key'])

        file_to_download = click.prompt("Enter the file name to download")
        local_directory = click.prompt("Enter the local directory to save the file")

        download_file(bucket, file_to_download, local_directory)

    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")

#------------------------------------------------------watch-------------------------------------------------------------------
def get_file_state(directory, recursive):
    file_state = set()
    for root, dirs, files in os.walk(directory):
        if not recursive and root != directory:
            break
        for file in files:
            file_state.add(os.path.relpath(os.path.join(root, file), directory))
    return file_state

@cli.command()
@click.option("--interval", default=1, help="Interval in seconds to check for file changes")
@click.option("--recursive/--no-recursive", default=False, help="Watch directory recursively")
@click.argument("directory", type=click.Path(exists=True))
def watch(interval, recursive, directory):
    click.echo(f"Watching directory: {directory}")
    click.echo("Press Ctrl+C to stop...")

    initial_state = get_file_state(directory, recursive)
    start_times = {}

    try:
        while True:
            current_state = get_file_state(directory, recursive)

            added_files = current_state - initial_state
            removed_files = initial_state - current_state
            modified_files = set()

            for file in initial_state & current_state:
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    modified_time = os.path.getmtime(file_path)
                    if modified_time > start_times.get(file, 0):
                        modified_files.add(file)
                        start_times[file] = modified_time

            if added_files:
                click.echo("Added files:")
                for file in added_files:
                    click.echo(f"- {file}")

            if removed_files:
                click.echo("REMOVED Files:")
                for file in removed_files:
                    click.echo(f"- {file}")

            if modified_files:
                click.echo("Modified files:")
                for file in modified_files:
                    click.echo(f"- {file}")

            initial_state = current_state
            time.sleep(interval)

    except KeyboardInterrupt:
        click.echo("Watch command stopped")

#----------------------------------------------------HELP COMMANDS---------------------------------------------------------

@cli.command()
def help():
    """Display help information for your script."""
    click.echo("--user\t\tFor accessing to create a Bucket ,Muliti-part Upload , Delete File and Listing files.")
    click.echo("--watch\t\tFor Watching the change of directory")
    click.echo("--help\t\tTo get access of all commands")
    # Add more general options if needed
    click.echo("For more information, run 'python your_script.py --help'")

if __name__ == '__main__':
    cli()
