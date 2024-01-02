import click
import boto3
import json
from botocore.exceptions import NoCredentialsError, ParamValidationError
from tabulate import tabulate

def enable_encryption_at_rest(bucket_name):
    try:
        s3 = boto3.client('s3')
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
        s3 = boto3.client('s3')
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

def view_s3_bucket_logs(bucket_name):
    try:
        # Enable encryption at rest and in transit
        enable_encryption_at_rest(bucket_name)
        enable_encryption_in_transit(bucket_name)

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

if __name__ == '__main__':
    # Replace 'your_bucket_name' with the actual bucket name
    view_s3_bucket_logs('your_bucket_name')
