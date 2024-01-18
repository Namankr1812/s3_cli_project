# S3 MULTI-PART OPERATION  CLI

The S3 CLI is a versatile command-line interface designed for interacting with Amazon Simple Storage Service (S3) buckets. This documentation provides a comprehensive guide to installing, configuring, and using the S3 CLI, along with key functionalities and additional notes for advanced usage.

## Table of Contents

1. [Installation and Configuration]
2. [Usage]
   - [User Setup]
   - [Bucket Operations]
   - [File Operations]
   - [Watch Command]
   - [Help Command]
3. [Additional Notes]

---

## 1. Installation and Configuration <a name="installation-and-configuration"></a>

### 1.1 Install Dependencies

Ensure Python is installed, then run:

```python
pip install click boto3
```
# Configuration 
Before using the S3 CLI, configure AWS credentials:

### 2.1 Using `aws configure`:

Run the following command in your terminal:

```python
aws configure
```
2.2 Set Environment Variables:
Alternatively, you can set environment variables for your AWS credentials. For example, add the following lines to your shell profile file (e.g., .bashrc, `.zshrc):
```python
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=your_region
```
---Ensure to replace your_access_key_id, your_secret_access_key, and your_region with your actual AWS credentials.

## 3. Usage 

### 3.1 User 

Prompt the user to set up an ID and password:

```python
user_id = click.prompt("Enter your user ID")
password = click.prompt("Enter your password", hide_input=True, confirmation_prompt=True)
```
### 3.2 Bucket Operations <a name="bucket-operations"></a>

#### 3.2.1 Create a New Bucket

```python
bucket = create_bucket()
```
Explanation:
    The user is prompted to create a new S3 bucket, and the create_bucket function is called.

### 3.2.2 List Existing Buckets
```python
existing_buckets = list_buckets()
```
Explanation:
    The script lists existing buckets using the list_buckets function.

### 3.2.3 Switch to a Different Bucket
```python
bucket = existing_buckets[selected_bucket_index - 1]
```
Explanation:
     The user is prompted to switch to a different bucket, and the selected bucket becomes the active bucket.

## 3.3 File Operations <a name="file-operations"></a>
### 3.3.1 Create a New Folder

```python
folder_name = click.prompt("Enter the folder name")
multi_part_new_folder_creation.create_folder(folder_name, bucket)
```
Explanation:
     The user is prompted to enter a folder name, and the create_folder function is called to create a new folder in the S3 bucket.

#### 3.3.2 Upload and List Files

```python
folder_path = click.prompt("Enter the folder path")
multi_part_upload.upload_folder(folder_path, bucket)
```
Explanation:
   The user is prompted to enter a folder path, and the upload_folder function is called to upload files from the specified folder to the S3 bucket.

### 3.3.3 List Folder Contents

```python
multi_part_list.list_folder_contents(bucket)
```
Explanation:
   The script lists the contents of a folder in the selected S3 bucket using the list_folder_contents function.

### 3.3.4 Delete Files Interactively

```python
files_to_delete = click.prompt("Enter the file names to delete (separated by space)").split()
multi_part_delete.delete_files_interactive(bucket, files_to_delete)
```
Explanation:
   The user is prompted to enter file names, and the delete_files_interactive function is called to delete the specified files from the S3 bucket.

### 3.3.5 Download a File from S3

```python
multi_part_download.download_from_s3(bucket)
```
Explanation:
   The download_from_s3 function is called to download a file from the selected S3 bucket.

### 3.3.6 View S3 Bucket Activity Logs

```python
multi_part_logs.view_s3_bucket_logs(bucket)
```
Explanation:
   The view_s3_bucket_logs function is called to display activity logs for the selected S3 bucket.

## 4. Watch Command 
### 4.1 Real-time File Monitoring

```python
python your_script.py watch --interval <seconds> --recursive/--no-recursive <directory>
```
Explanation:
   The watch command monitors file changes in the specified directory, with options for setting the interval and enabling recursive watching.

### 5. Help Command <a name="help-command"></a>

#### 5.1 Display Script Information

```python
python your_script.py help
```
Explanation:
   The help command displays information about the script and its available commands.

## 6. Additional Notes <a name="additional-notes"></a>
### 6.1 Encryption Options

Enable Encryption at Rest:


```python
Function: enable_encryption_at_rest(bucket_name)

```
**6.2 File Hash Calculation**
Function to calculate SHA-256 hash of a specified file.
**6.3 Error Handling**
Comprehensive error handling for missing credentials and parameter validation errors.
**6.4 Watch Command**
Real-time monitoring of file changes in the specified directory.
**6.5 Logging**
Logging of errors and important events using the Python logging module.

### 6.1 Encryption Options

#### 6.1.1 Enable Encryption at Rest

```python
def enable_encryption_at_rest(bucket_name):
    try:
        # AWS S3 Client Initialization
        s3 = session.client('s3')

        # Enabling Encryption at Rest
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

        # Success Message
        click.echo(f"Encryption at rest enabled for {bucket_name}.")

    except NoCredentialsError:
        # Missing Credentials Error Handling
        click.echo("Credentials not available. Please set up your AWS credentials.")

    except ParamValidationError as e:
        # Parameter Validation Error Handling
        click.echo(f"Error enabling encryption at rest: {str(e)}")
        logging.error(f"Error enabling encryption at rest: {str(e)}")
```
#### 6.1.1 Enable Encryption at Rest

**Explanation:**

- **AWS S3 Client Initialization:** The function initializes an S3 client using the existing session.
- **Enabling Encryption at Rest:** It uses the `put_bucket_encryption` method to enable encryption at rest for the specified S3 bucket.
    - The encryption configuration includes a rule specifying the default server-side encryption algorithm (**AES256** in this case).
- **Success Message:** If the encryption at rest is successfully configured, it prints a success message using `click.echo`.
- **Error Handling - Missing Credentials:** The function catches `NoCredentialsError` and prints a message indicating that AWS credentials are not available. This ensures that the user is informed to set up AWS credentials.
- **Error Handling - Parameter Validation:** It catches `ParamValidationError` and prints an error message, providing information about the validation error that occurred during the attempt to enable encryption at rest.
    - Additionally, it logs the error using the logging module for more detailed error tracking.

**Overview:**

This function is responsible for configuring and enabling encryption at rest for a specified S3 bucket.
It utilizes the `put_bucket_encryption` method, providing the necessary encryption configuration.
Success and error messages are displayed to the user, and in case of errors, details are logged for further analysis.
The error handling ensures that the user is informed about any issues that may arise during the process of enabling encryption at rest.

---

### 6.1.2 Enable Encryption in Transit

```python
# Enable Encryption in Transit

def enable_encryption_in_transit(bucket_name):
    try:
        # **AWS S3 Client Initialization:**
        s3 = session.client('s3')

        # **Configuring Bucket Policy for Encryption in Transit:**
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=f'''{{
                "Version": "2012-10-17",
                "Id": "PutObjPolicy",
                "Statement": [
                    {{
                        "Effect": "Deny",
                        "Principal": "*",
                        "Action": "s3:*",
                        "Resource": [
                            "arn:aws:s3:::{bucket_name}/*"
                        ],
                        "Condition": {{
                            "Bool": {{
                                "aws:SecureTransport": "false"
                            }}
                        }}
                    }}
                ]
            }}'''
        )

        # **Success Message:**
        click.echo(f"Encryption in transit enabled for {bucket_name}.")

    except NoCredentialsError:
        # **Missing Credentials Error Handling:**
        click.echo("Credentials not available. Please set up your AWS credentials.")

    except ParamValidationError as e:
        # **Parameter Validation Error Handling:**
        click.echo(f"Error enabling encryption in transit: {str(e)}")
        logging.error(f"Error enabling encryption in transit: {str(e)}")

```
**Explanation:**

- **AWS S3 Client Initialization:**
  - The function initializes an S3 client using the existing session.

- **Configuring Bucket Policy for Encryption in Transit:**
  - It uses the `put_bucket_policy` method to configure a bucket policy for the specified S3 bucket.
  - The policy, written in JSON format, includes a statement that denies actions on objects in the bucket when not accessed via a secure transport (HTTPS).
  - The condition `"aws:SecureTransport": "false"` ensures that the denial applies when not accessed securely.

- **Success Message:**
  - If the policy is successfully configured, it prints a success message using `click.echo`.

- **Error Handling - Missing Credentials:**
  - The function catches `NoCredentialsError` and prints a message indicating that AWS credentials are not available. This ensures that the user is informed to set up AWS credentials.

- **Error Handling - Parameter Validation:**
  - It catches `ParamValidationError` and prints an error message, providing information about the validation error that occurred during the attempt to enable encryption in transit.
  - Additionally, it logs the error using the logging module for more detailed error tracking.

**Overview:**

This function is responsible for configuring and enabling encryption in transit for a specified S3 bucket. It achieves this by setting a bucket policy that denies access to objects when accessed over an insecure transport. Success and error messages are displayed to the user, and in case of errors, details are logged for further analysis. The error handling ensures that the user is informed about any issues that may arise during the process of enabling encryption in transit.


### 6.1.3 Enable Client-Side Encryption

```python
# Enable Client-Side Encryption

**def enable_client_side_encryption_auto(bucket_name):**
    **try:**
        **s3 = session.client('s3')**

        **# Enable client-side encryption automatically**
        **s3.put_bucket_encryption(**
            **Bucket=bucket_name,**
            **ServerSideEncryptionConfiguration={**
                **'Rules': [**
                    **{**
                        **'ApplyServerSideEncryptionByDefault': {**
                            **'SSEAlgorithm': 'aws:kms'**
                        **}**
                    **}**
                **]**
            **}**
        **)**

        **click.echo(f"Encryption setup completed for {bucket_name}.")**

    **except NoCredentialsError:**
        **click.echo("Credentials not available. Please set up your AWS credentials.")**

    **except Exception as e:**
        **click.echo(f"Error enabling client-side encryption: {str(e)}")**
        **logging.error(f"Error enabling client-side encryption: {str(e)}")**
```
**AWS S3 Client Initialization:**

The function initializes an S3 client using the existing session.

**Configuring Bucket Encryption:**

It uses the `put_bucket_encryption` method to configure encryption for the specified S3 bucket.

The configuration includes a rule with `ApplyServerSideEncryptionByDefault`, specifying the use of AWS Key Management Service (KMS) for server-side encryption.

**Success Message:**

If the encryption setup is successful, it prints a success message using `click.echo`.

**Error Handling - Missing Credentials:**

The function catches `NoCredentialsError` and prints a message indicating that AWS credentials are not available. This ensures that the user is informed to set up AWS credentials.

**Generic Error Handling:**

It catches a general `Exception` and prints an error message, providing information about the error that occurred during the attempt to enable client-side encryption.

Additionally, it logs the error using the logging module for more detailed error tracking.

**Overview:**

This function is responsible for automatically configuring and enabling client-side encryption for a specified S3 bucket. It achieves this by setting up a server-side encryption configuration that applies encryption by default using AWS Key Management Service (KMS). Success and error messages are displayed to the user, and in case of errors, details are logged for further analysis. The error handling ensures the user is informed about any issues that may arise while enabling client-side encryption.

**6.1.4. Enable HSM Protection:**

The `enable_hsm_protection` function enables Hardware Security Module (HSM) protection for an S3 bucket using AWS KMS.

```markdown
```python
def enable_hsm_protection(bucket_name):
    try:
        kms_client = session.client('kms')

        # Create a new AWS KMS key for HSM protection
        response = kms_client.create_key(
            Description='KMS key for S3 HSM protection',
            KeyUsage='ENCRYPT_DECRYPT',
            Origin='AWS_KMS'
        )
        kms_key_id = response['KeyMetadata']['KeyId']

        # Allow S3 to use the key for HSM protection
        kms_client.put_key_policy(
            KeyId=kms_key_id,
            PolicyName='default',
            Policy=json.dumps({
                'Version': '2012-10-17',
                'Id': 'key-default-1',
                'Statement': [
                    {
                        'Effect': 'Allow',
                        'Principal': '*',
                        'Action': 'kms:*',
                        'Resource': '*'
                    }
                ]
            })
        )

        # Enable client-side encryption using the KMS key
        enable_client_side_encryption_auto(bucket_name)

        click.echo(f"HSM protection using AWS KMS enabled for {bucket_name}.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"Error enabling HSM protection: {str(e)}")
        logging.error(f"Error enabling HSM protection: {str(e)}")
```

**AWS KMS Client Initialization:**

The function initializes an AWS Key Management Service (KMS) client using the existing session.

**Creating KMS Key for HSM Protection:**

It creates a new KMS key with specific properties, such as usage for encryption and decryption and origin as AWS Key Management Service.

**Key Policy Configuration:**

The function sets a key policy that allows S3 to use the newly created KMS key for HSM protection. This is done using the `put_key_policy` method.

**Enabling Client-Side Encryption with KMS Key:**

It calls the `enable_client_side_encryption_auto` function, passing the S3 bucket name. This function configures and enables client-side encryption using the KMS key.

**Success Message:**

If the HSM protection setup is successful, it prints a success message using `click.echo`.

**Error Handling - Missing Credentials:**

The function catches `NoCredentialsError` and prints a message indicating that AWS credentials are not available. This ensures that the user is informed to set up AWS credentials.

**Generic Error Handling:**

It catches a general `Exception` and prints an error message, providing information about the error that occurred during the attempt to enable HSM protection.

Additionally, it logs the error using the logging module for more detailed error tracking.

**Overview:**

This function is responsible for enabling Hardware Security Module (HSM) protection for an S3 bucket using AWS Key Management Service (KMS).
It creates a new KMS key, configures a policy to allow S3 to use the key, and then enables client-side encryption using the KMS key.
Success and error messages are displayed to the user, and in case of errors, details are logged for further analysis.
The function ensures that the user is informed about any issues that may arise during the process of enabling HSM protection.

**6.1.5File Hash Calculation:**

The `calculate_file_hash` function calculates the SHA-256 hash of a specified file.

```python
def calculate_file_hash(file_path, block_size=65536):
    sha256 = hashlib.sha256()

    with open(file_path, 'rb') as file:
        for block in iter(lambda: file.read(block_size), b''):
            sha256.update(block)

    return sha256.hexdigest()

**Explanation:**

The function reads the file in blocks and updates the SHA-256 hash using the hashlib library.

The **hexdigest** method returns the hexadecimal representation of the hash.

**Code:**

```python
file_path = r"D:\multipart_upload\client\client.py"

try:
    hash_value = calculate_file_hash(file_path)
    print(f"SHA-256 hash of {file_path}: {hash_value}")
except Exception as e:
    print(f"Error calculating hash: {e}")
**Error Handling:**

The script includes error handling to manage various scenarios, such as missing credentials and parameter validation errors. For example:

**Explanation:**

The `NoCredentialsError` exception is caught when AWS credentials are not available.

The `ParamValidationError` exception is caught for errors related to parameter validation, such as invalid input.

The script uses `try`, `except`, and logging to handle errors gracefully, providing informative messages to the user and logging detailed error information.
```



# S3 CLI Script Documentation

This documentation provides a detailed explanation of the S3 CLI script, covering key functionalities, encryption, file upload, and error handling.

## Table of Contents

1. [Introduction](#introduction)
2. [Dependencies](#dependencies)
3. [Encryption](#encryption)
4. [Encryption Keys Management](#encryption-keys-management)
5. [Data Encryption and Decryption](#data-encryption-and-decryption)
6. [Key Generation](#key-generation)
7. [File Upload](#file-upload)
8. [S3 Endpoint Retrieval](#s3-endpoint-retrieval)
9. [Part Upload](#part-upload)
10. [Parallel Uploads](#parallel-uploads)
11. [Upload Completion](#upload-completion)
12. [Encryption Key Saving](#encryption-key-saving)
13. [Error Handling](#error-handling)
14. [Conclusion](#conclusion)

##Introduction
The S3 CLI script is a command-line interface for interacting with Amazon Simple Storage Service (S3).
It facilitates the creation of S3 buckets, uploads files, and provides options for encryption at rest and in transit.
The script incorporates multi-part upload for efficient handling of large files and client-side encryption.
```
```python
Dependencies
- click
- boto3
- os
- time
- math
- datetime
- uuid
- logging
- hashlib
- sys
- cryptography
- botocore.exceptions (NoCredentialsError)
- concurrent.futures (ThreadPoolExecutor, as_completed)
- click (prompt)
- tabulate
- boto3.s3.transfer (TransferConfig)
- cryptography.fernet (Fernet)
- cryptography.hazmat.backends (default_backend)
- cryptography.hazmat.primitives (hashes)
- cryptography.hazmat.primitives.kdf.pbkdf2 (PBKDF2HMAC)
- base64
- json
```

Here, we import necessary libraries and modules:

- **click:** for command-line interface creation.
- **boto3:** the AWS SDK for Python.
- **os:** for interacting with the operating system.
- **time, datetime:** for handling timestamps and time-related operations.
- **uuid:** for generating unique identifiers.
- **logging:** for logging messages.
- **hashlib:** for hashing data.
- **sys:** for accessing Python interpreter variables.
- **cryptography:** for cryptographic functions.
- **NoCredentialsError:** an exception from botocore.exceptions indicating missing AWS credentials.
- **ThreadPoolExecutor, as_completed:** for parallel execution.
- **prompt:** a function from click for user prompts.
- **tabulate:** for formatting tabular data.
- **TransferConfig:** a configuration class for S3 transfers.

2. **Session and S3 Resource Initialization**

   ```python
   session = boto3.Session()
   s3 = session.resource('s3')
Explanation:
Here, an AWS session and S3 resource are established using boto3. The session allows for configuration, and the S3 resource enables interaction with the S3 service.

3. **Encryption Keys Dictionary:**

```python
# Dictionary to store encryption keys for each file
encryption_keys = {}
```
Explanation:
encryption_keys is a Python dictionary used to store encryption keys associated with each file. This centralized storage simplifies key management during file processing.

4. **Functions for Loading and Saving Encryption Keys:**

```python
# Function to load encryption keys from a JSON file
def load_encryption_keys():
    try:
        with open('encryption_keys.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Function to save encryption keys to a JSON file
def save_encryption_keys():
    try:
        with open('encryption_keys.json', 'w') as file:
            keys_dict = {key: encryption_keys[key].decode('latin1') for key in encryption_keys}
            json.dump(keys_dict, file)
    except Exception as e:
        print(f"Error saving encryption keys: {e}")
```
**Explanation:**

**load_encryption_keys Function:**

**Opening JSON File:**
The function attempts to open the 'encryption_keys.json' file for reading using a with statement, ensuring proper file handling.

**Loading JSON Content:**
It uses the json.load method to parse the content of the JSON file. This content is expected to be a dictionary containing encryption keys.

**Handling File Not Found or JSON Decode Error:**
If the file is not found (raises FileNotFoundError) or if there is an issue decoding the JSON content (raises JSONDecodeError), the function returns an empty dictionary ({}).


**save_encryption_keys Function:**

**Opening JSON File for Writing:**
The function attempts to open the 'encryption_keys.json' file for writing, creating a new file if it doesn't exist, using a with statement.

**Creating Dictionary for JSON Dump:**
It creates a dictionary (keys_dict) by iterating over the encryption_keys dictionary and decoding each key using the 'latin1' encoding. The resulting dictionary is suitable for JSON serialization.

**Saving Encrypted Keys to JSON File:**
The json.dump method is used to write the dictionary (keys_dict) to the opened file in JSON format.

**Handling Exceptions:**
If any exception occurs during the file writing process, it catches the generic Exception type and prints an error message indicating the issue.

**Overview:**
These functions together provide a mechanism to load encryption keys from a JSON file (load_encryption_keys) and save encryption keys to a JSON file (save_encryption_keys). This is particularly useful for persisting encryption keys between sessions or storing them for future use. The functions gracefully handle scenarios where the file is not found or there are issues with the JSON decoding and saving processes. Any exceptions during the saving process are caught, and an error message is printed to inform the user about the error.

5. **Function to Get S3 Endpoint:**

   ```python
   # Function to get the S3 endpoint for a given bucket
   def get_s3_endpoint(bucket_name):
       try:
           client = boto3.client('s3')
           location = client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
           return f'https://s3.{location}.amazonaws.com'
       except Exception as e:
           print(f"Error getting S3 endpoint: {e}")
           return 'https://s3.amazonaws.com'  # Default to global S3 endpoint
**Explanation:**

This function, `get_s3_endpoint`, is designed to retrieve the S3 endpoint for a given bucket. The process involves creating an S3 client using `boto3.client('s3')` and then using the `get_bucket_location` method to determine the bucket's location.

- **Client Initialization:**
  The function initializes an S3 client using `boto3.client('s3')`.

- **Get Bucket Location:**
  It calls `client.get_bucket_location` with the specified `bucket_name` to retrieve the location of the bucket.

- **Construct S3 Endpoint URL:**
  The S3 endpoint URL is constructed based on the bucket's location, and the function returns this URL.

- **Error Handling:**
  If any exception occurs during the process (e.g., the bucket does not exist or there is an issue with the S3 client), the function catches the exception, prints an error message, and defaults to the global S3 endpoint (`'https://s3.amazonaws.com'`).

**Overview:**

This function is essential for dynamically determining the S3 endpoint associated with a specific bucket. It allows flexibility for different regions and ensures correct endpoint construction. Any errors during the process are handled gracefully, and the function provides a default global S3 endpoint in case of issues.

This function determines the appropriate S3 endpoint based on the specified bucket's location. It defaults to the global S3 endpoint if the location is not available.


**calculate_number_of_parts:**
```python
# Function to calculate the number of parts for a given file size and part size
def calculate_number_of_parts(file_size, part_size):
    return (file_size + part_size - 1) // part_size
```
**Explanation:**
This function calculates the number of parts needed to split a file based on its size and the desired part size. It ensures that each part, except possibly the last one, is of the specified part size.

**7. Functions for Encrypting and Decrypting Data:**

```python
# Function to encrypt data using Fernet symmetric encryption
def encrypt_data(data, encryption_key):
    salt = b'salt_123'  # Change this to a unique value
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        iterations=100000,
        salt=salt,
        length=32,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(encryption_key))
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data)
    return encrypted_data, key  # Return the encrypted data along with the key

# Function to decrypt data using Fernet symmetric decryption
def decrypt_data(data, encryption_key):
    try:
        cipher = Fernet(encryption_key)
        decrypted_data = cipher.decrypt(data)
        return decrypted_data
    except Exception as e:
        click.echo(f"Error decrypting data: {str(e)}")
        return b''  # Return an empty byte string in case of decryption failure
```
**Explanation: ENCRYPTION**

**Salt Generation:**
A salt is introduced to the encryption process, and in this case, it's set to a constant value (`b'salt_123'`). For heightened security, it's essential to use a unique salt for each encryption operation. A salt is a random value used to add complexity to the encryption process, making it more secure. Here, the salt is set to a constant value `b'salt_123'`, but for actual use, it should be unique for each encryption.

**Key Derivation Function (KDF):**
The `PBKDF2HMAC` function is a key derivation function used to stretch the provided encryption key. It applies the SHA-256 hashing algorithm, undergoes 100,000 iterations, and produces a derived key of length 32 bytes. This process strengthens the key and makes it more resilient to brute-force attacks.

**Base64 Encoding of Key:**
The derived key is then base64 encoded. Base64 encoding ensures that the key can be safely represented using ASCII characters, making it suitable for storage and transmission.

**Fernet Cipher Initialization:**
With the derived key in hand, a Fernet cipher is initialized. Fernet is a symmetric encryption algorithm that uses the same key for both encryption and decryption. The initialized cipher is ready to perform encryption using the derived key.

**Encryption:**
The actual encryption occurs using the Fernet cipher. The provided data is encrypted, resulting in `encrypted_data`. Both the encrypted data and the key used for encryption are returned. This design allows the calling code to retain the key for decryption purposes.

By incorporating salt, a key derivation function, and the Fernet symmetric encryption algorithm, this encryption process strengthens the security of sensitive data, making it more resistant to various cryptographic attacks. The use of a derived key, rather than the original key, adds an additional layer of security.

**Explanation: DECRYPTION**

**Cipher Initialization:**
The Fernet cipher is initialized for decryption using the provided encryption key. This key should match the key used for the corresponding encryption. The initialization is a crucial step in preparing the cipher for the decryption process.

**Decryption Attempt:**
The `decrypt` method of the Fernet cipher is invoked with the encrypted data. This method attempts to reverse the encryption process, using the provided key. If successful, it returns the decrypted data.

**Error Handling:**
A try-except block is implemented to catch exceptions that might occur during decryption. Various issues could lead to decryption failure, such as an incorrect key or corrupted encrypted data. If an exception is caught, the error message is printed using `click.echo`, providing information about the decryption failure.

**Fallback Response:**
In case of a decryption failure, an empty byte string (`b''`) is returned. This is a deliberate design choice to ensure that the calling code receives a consistent response even in error scenarios. It allows the calling code to identify decryption failures and handle them gracefully.

**Overview:**
These functions, when used together, enable the secure encryption and decryption of data using the Fernet symmetric encryption algorithm. The initialization of the Fernet cipher ensures that the decryption key is correctly set. Error handling is implemented to catch and report any issues that may arise during decryption. The inclusion of a fallback response, an empty byte string, ensures that the calling code can reliably handle decryption failures. The use of a key derivation function and a unique salt adds an additional layer of security to the overall encryption and decryption processes.

**8. Function to Generate Encryption Key:**

```python
# Function to generate a random encryption key
def generate_encryption_key():
    return os.urandom(32)
```
**Explanation:**

This function generates a random encryption key of 32 bytes using `os.urandom()`. It ensures a high level of randomness for security. The use of a secure random source is crucial in creating encryption keys to prevent predictability and enhance the overall security of the encryption process.

# Function to upload a part of a file to S3
def upload_part(args, bucket_region='us-east-1'):
    part_number, upload_id, file_path, bucket, file_name, part_size = args
    s3_endpoint = get_s3_endpoint(bucket)

    with open(file_path, 'rb') as file:
        file.seek(part_size * (part_number - 1))
        data = file.read(part_size)

        # Retrieve or generate encryption key for the file
        encryption_key = encryption_keys.get(file_name)
        if not encryption_key:
            encryption_key = generate_encryption_key()
            encryption_keys[file_name] = encryption_key

        # Check if client-side encryption is enabled
        if encryption_key:
            encrypted_data, key = encrypt_data(data, encryption_key)
            encryption_keys[file_name] = key  # Update the key in case it was newly generated
        else:
            encrypted_data = data

        # Specify the server-side encryption algorithm
        s3 = boto3.client('s3', endpoint_url=s3_endpoint, region_name=bucket_region)

        # Use 'Body' directly in the arguments
        s3_upload_args = {
            'Bucket': bucket,
            'Key': file_name,
            'UploadId': upload_id,
            'PartNumber': part_number,
            'Body': encrypted_data,
        }

        try:
            response = s3.upload_part(**s3_upload_args)
        except Exception as e:
            click.echo(f"An error occurred: {str(e)}")
            return {"PartNumber": part_number, "Error": str(e)}

    etag = response["ETag"]
    return {"PartNumber": part_number, "ETag": etag}

**File Reading**
The function starts by opening the specified file (`file_path`) in binary mode (`'rb'`). 
It seeks to the appropriate position based on the part number and reads the data with a size equal to the specified part size.

**Encryption Key Handling**
It retrieves or generates the encryption key for the file.
If the encryption key is not already stored in the `encryption_keys` dictionary, a new one is generated using the `generate_encryption_key` function.
The encryption key is then updated in the dictionary.

**Client-Side Encryption**
If client-side encryption is enabled (i.e., an encryption key exists), the data is encrypted using the `encrypt_data` function.
The updated encryption key is stored in the `encryption_keys` dictionary.

**Server-Side Encryption Specification**
The function specifies the server-side encryption algorithm and creates a connection to Amazon S3 using the specified endpoint and region.

**S3 Upload Configuration**
The parameters for uploading the part to S3 are configured in the `s3_upload_args` dictionary.
This includes the bucket, key (file name), upload ID, part number, and the body of the request, which is the encrypted data.

**Part Upload**
The part is uploaded to Amazon S3 using the `upload_part` method from the S3 client.
This method sends a part of the file to be assembled later during the multipart upload.

**Error Handling**
A try-except block is implemented to catch exceptions that might occur during the upload process.
If an exception occurs, an error message is printed using `click.echo`, and a dictionary indicating the part number and the error is returned.

**ETag Retrieval**
If the upload is successful, the ETag (entity tag) of the uploaded part is retrieved from the S3 response.

**Result Return**
A dictionary containing the part number and ETag is returned if the upload is successful.

# 10. Main Function for Uploading a Folder

```python
# Main function for uploading files in a folder to S3

@click.option("--target-part-size", default=None, type=int, help="Size of each part in bytes")
@click.option("--num-parts", default=None, type=int, help="Number of parts for each file")
def upload_folder(folder_path, bucket, target_part_size=None, num_parts=None):

    try:
        # Get S3 bucket region
        s3_bucket = boto3.resource('s3').Bucket(bucket)
        bucket_region = s3_bucket.meta.client.meta.region_name

        # Use the correct S3 endpoint for the specified region
        s3_endpoint = get_s3_endpoint(bucket)

        # Upload files in the folder
        s3 = boto3.client('s3', endpoint_url=s3_endpoint, region_name=bucket_region)
        parts_total = []

        # Get a list of all files in the folder
        file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if
                      os.path.isfile(os.path.join(folder_path, file))]

        # Prompt the user for the number of parts and part size
        if target_part_size is None or num_parts is None:
            total_file_size = sum(os.path.getsize(file) for file in file_paths)

            # Calculate the default part size based on file size
            default_part_size = min(max(5 * 1024 * 1024, total_file_size // 100), 100 * 1024 * 1024)
            click.echo(f"Default part size: {default_part_size} bytes")

            # Prompt the user for part size if not provided
            target_part_size = click.prompt("Enter part size (in bytes)", default=default_part_size, type=int)

            # Ensure the part size meets the minimum requirement
            target_part_size = max(target_part_size, 5 * 1024 * 1024)

            # Prompt the user for the number of parts if not provided
            num_parts = click.prompt("Enter the number of parts for all files", default=num_parts, type=int)

        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            response = s3.create_multipart_upload(Bucket=bucket, Key=file_name)
            upload_id = response['UploadId']

            # Calculate part size based on file size and user input
            file_size = os.path.getsize(file_path)

            # Adjust part size based on file size
            part_size = min(target_part_size, file_size)

            # Calculate the number of parts based on the adjusted part size
            num_parts = calculate_number_of_parts(file_size, part_size)

            # Use ThreadPoolExecutor for parallel uploads with increased workers
            with ThreadPoolExecutor(max_workers=10) as executor:
                args_list = [(part_number, upload_id, file_path, bucket, file_name, part_size)
                             for part_number in range(1, num_parts + 1)]

                # Upload parts in parallel
                parts = list(executor.map(lambda args: upload_part(args, bucket_region), args_list))

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
            click.echo(f"{file_name} uploaded successfully. Encryption Key: {encryption_keys[file_name]}")

        click.echo("All files in the folder uploaded successfully.")

        # Save the encryption keys at the end of the upload process
        save_encryption_keys()

        # List contents of the bucket
        try:
            s3_bucket = boto3.resource('s3').Bucket(bucket)
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
```
**AWS Resources Initialization:**

The function initializes AWS resources, including creating an S3 client and getting the S3 bucket region.

**S3 Endpoint Determination:**

It determines the correct S3 endpoint based on the specified bucket.

**File Discovery:**

The function lists all files in the specified folder and constructs their full paths.

**User Input Prompting:**

If target part size or the number of parts is not provided, the function prompts the user to input values, ensuring the part size meets the minimum requirement.

**Multipart Upload Initialization:**

For each file, it initiates a multipart upload on the S3 bucket, obtaining an upload ID.

**Parallel Upload Execution:**

Utilizing ThreadPoolExecutor, the function concurrently uploads parts of files in parallel. Each part is uploaded using the `upload_part` function.

**Error Handling during Upload:**

The function checks for errors in the uploaded parts. If errors are detected, it prints error messages and raises an exception to signify a failed upload.

**Multipart Upload Completion:**

Once all parts are successfully uploaded, the function completes the multipart upload, assembling the file on S3.

**Information Display:**

Information about successful uploads, including file names and encryption keys, is displayed using `click.echo`.

**Encryption Key Storage:**

The function saves encryption keys at the end of the upload process using the `save_encryption_keys` function.

**Bucket Contents Listing:**

It lists the contents of the S3 bucket after the upload process, displaying object keys.

**Error Handling for Various Scenarios:**

The function is wrapped in try-except blocks to handle different types of errors gracefully. If the folder doesn't exist, AWS credentials are missing, or any other unexpected error occurs, informative messages are displayed.

**Overview:**

This function serves as the orchestration point for uploading files from a specified folder to an S3 bucket. 
It handles various tasks, including AWS resource initialization, multipart upload management, error handling, and informative display of upload results. 
The user is prompted for input when necessary, and the function ensures the secure and reliable transfer of files to the designated S3 bucket.

**11. Documentation Summary**

This part of the documentation summarizes the key features of the script, including upload completion, encryption key saving, and robust error handling. It emphasizes the script's utility for secure and efficient interactions with Amazon S3, particularly for large files with client-side encryption and multi-part uploads.

# Secure S3 File Download Operations Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Encryption Mechanism](#encryption-mechanism)
6. [Key Management](#key-management)
7. [Enabling Encryption at Rest](#enabling-encryption-at-rest)
8. [Enabling Encryption in Transit](#enabling-encryption-in-transit)
9. [Client-Side Encryption](#client-side-encryption)
10. [HSM Protection](#hsm-protection)
11. [File Download Process](#file-download-process)
12. [Usage Examples](#usage-examples)
13. [Conclusion](#conclusion)

# Introduction

The S3 CLI script is a command-line interface for interacting with Amazon Simple Storage Service (S3). 
It facilitates the creation of S3 buckets, uploads files, and provides options for encryption at rest and in transit. 
The script incorporates multi-part upload for efficient handling of large files and client-side encryption.

## 1. Imports

```python
import click
import boto3
import os
import time
import math
import datetime
import uuid
import logging
import hashlib
import sys
import cryptography

from botocore.exceptions import NoCredentialsError
from concurrent.futures import ThreadPoolExecutor, as_completed
from click import prompt
from tabulate import tabulate
from boto3.s3.transfer import TransferConfig
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
```
**Click**

A Python package for creating command-line interfaces.

**Boto3**

The Amazon Web Services (AWS) SDK for Python, providing interfaces for AWS services.

**OS**

Provides a way of interacting with the operating system, here used for creating directories.

**Base64**

For encoding and decoding base64 data.

**JSON**

Handling JSON files.

**Botocore Exceptions**

Exceptions related to Boto3.

**Fernet**

A symmetric encryption algorithm for securing data.

**Cryptography**

A library for secure communication and data storage.

## 2.AWS Session Initialization

```python
session = boto3.Session()
s3 = session.resource('s3')
```
**Boto3 Session Initialization:**
Explanation:
- The code initializes an AWS session using the boto3.Session() constructor. A session serves as a way to manage state about a particular set of AWS credentials.

**S3 Resource:**
Explanation:
- The s3 variable is created as an instance of the S3 resource. In Boto3, a resource is a high-level object-oriented API for interacting with AWS services. In this case, it represents an Amazon S3 resource, allowing high-level operations on S3 buckets and objects. The session.resource('s3') call sets up the S3 resource using the previously initialized AWS session.

# 3.Dictionary to store encryption keys for each file
```python
encryption_keys = {}
```
**Explanation:**

- **Dictionary:** Holds encryption keys for each file. This is crucial for managing and using keys during encryption and decryption processes.

- **Note:**This dictionary serves as a central repository for storing encryption keys. It is designed to facilitate easy retrieval and management of keys associated with different files, providing a systematic approach to key handling in the script.

# 4.Function to load encryption keys from a JSON file
```python
def load_encryption_keys():
    try:
        with open('encryption_keys.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
```
# Function to save encryption keys to a JSON file
```python
def save_encryption_keys():
    try:
        with open('encryption_keys.json', 'w') as file:
            keys_dict = {key: encryption_keys[key].decode('latin1') for key in encryption_keys}
            json.dump(keys_dict, file)
    except Exception as e:
        print(f"Error saving encryption keys: {e}")
```
**Explanation**
- **Load Encryption Keys:** This function reads encryption keys from a JSON file using the `load_encryption_keys` function. It attempts to open the 'encryption_keys.json' file for reading, and if successful, it uses `json.load` to parse the content of the JSON file. If the file is not found (raises `FileNotFoundError`) or if there is an issue decoding the JSON content (raises `JSONDecodeError`), the function returns an empty dictionary (`{}`).

- **Save Encryption Keys:** This function writes encryption keys to a JSON file using the `save_encryption_keys` function. It attempts to open the 'encryption_keys.json' file for writing, creating a new file if it doesn't exist. It creates a dictionary (`keys_dict`) by iterating over the `encryption_keys` dictionary and decoding each key using the 'latin1' encoding. The resulting dictionary is suitable for JSON serialization. The `json.dump` method is then used to write the dictionary to the opened file in JSON format. If any exception occurs during the file writing process, it catches the generic `Exception` type and prints an error message indicating the issue.

# 5.Enable Encryption at Rest: 
```python
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
    except Exception as e:
        click.echo(f"Error enabling encryption at rest: {str(e)}")
```

- **Enable Encryption at Rest:** Uses AWS SDK (boto3) to configure encryption at rest for an S3 bucket. 

# 6.Enable Encryption in Transit:
```python
def enable_encryption_in_transit(bucket_name):
    try:
        s3 = session.client('s3')
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=f'''{{
                "Version": "2012-10-17",
                "Id": "PutObjPolicy",
                "Statement": [
                    {{
                        "Effect": "Deny",
                        "Principal": "*",
                        "Action": "s3:*",
                        "Resource": [
                            "arn:aws:s3:::{bucket_name}/*"
                        ],
                        "Condition": {{
                            "Bool": {{
                                "aws:SecureTransport": "false"
                            }}
                        }}
                    }}
                ]
            }}'''
        )
        click.echo(f"Encryption in transit enabled for {bucket_name}.")
    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"Error enabling encryption in transit: {str(e)}")
```
- **Enable Encryption in Transit:** Uses AWS SDK (boto3) to configure a bucket policy denying non-secure transport. 

# 7.Get S3 Endpoint:
```python
def get_s3_endpoint(bucket_name):
    try:
        client = boto3.client('s3')
        location = client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        return f'https://s3.{location}.amazonaws.com'
    except Exception as e:
        print(f"Error getting S3 endpoint: {e}")
        return 'https://s3.amazonaws.com'  # Default to the global S3 endpoint
```

- **Get S3 Endpoint:** Determines the S3 endpoint based on the bucket's location. 

# 8.Enable Encryption:
```python
def enable_encryption(bucket_name):
    click.echo(f"Enabling encryption for {bucket_name}...")
    enable_encryption_at_rest(bucket_name)
    enable_encryption_in_transit(bucket_name)
```

- **Enable Encryption:** Calls functions to enable both encryption at rest and encryption in transit. 

# 9.Validate and Decode Key:
```python
def validate_and_decode_key(encoded_key):
    try:
        # Add padding characters ('=') if needed
        encoded_key += '=' * (4 - len(encoded_key) % 4)

        # Decode the base64-encoded key
        decoded_key = base64.urlsafe_b64decode(encoded_key.encode())

        # Ensure the key is 32 bytes
        if len(decoded_key) != 32:
            raise ValueError("Invalid key length. The key must be 32 bytes.")

        return decoded_key

    except Exception as e:
        raise ValueError(f"Error validating and decoding key: {str(e)}")
```

- **Padding for Base64 Encoding:**

The function checks if the length of the encoded key is not a multiple of 4. 

If not, it adds padding characters ('=') to make the length a multiple of 4. This is a requirement for proper base64 decoding. 

- **Base64 Decoding:** 

The base64-encoded key is decoded using base64.urlsafe_b64decode. The urlsafe variant is used, which replaces '+' and '/' with '-' and '_', respectively. 

- **Key Length Validation:** 

After decoding, the function ensures that the length of the decoded key is exactly 32 bytes. 

If the length is not 32 bytes, it raises a ValueError indicating that the key length is invalid. 

- **Exception Handling:** 

The function is wrapped in a try-except block to catch any exceptions that might occur during the decoding and validation process. 

If an exception occurs, it raises a ValueError with an informative error message indicating the issue. 

- **Purpose of the Function:** 

The purpose of this function is to take a base64-encoded key, ensure it has the correct length (32 bytes), and return the decoded key. This is crucial for ensuring that the encryption keys used in the application are in the expected format and size before being used for cryptographic operations. The function provides a robust mechanism to handle potential issues during the decoding and validation process, raising descriptive errors if something goes wrong. 

In the context of cryptographic operations, having a valid and correctly sized key is essential for the security and integrity of the encryption process. Any deviation from the expected key length could result in cryptographic vulnerabilities or errors during encryption or decryption. Therefore, this function serves as a critical step in preparing keys for use in the encryption and decryption procedures elsewhere in the code.  

# 10.Decrypt Data:
```python
def decrypt_data(data, encryption_key):
    try:
        cipher = Fernet(encryption_key)
        decrypted_data = cipher.decrypt(data)
        return decrypted_data

    except Exception as e:
        click.echo(f"Error decrypting data: {str(e)}")
        return b''  # Return an empty byte string in case of decryption failure
```

**Steps Explained:**

- **Cipher Initialization:** 

The function initializes a Fernet cipher by providing it with the encryption key passed as an argument. Fernet is a symmetric encryption algorithm that requires the same key for both encryption and decryption. 

- **Decryption Attempt:** 

The decrypt method of the Fernet cipher is called with the provided data to attempt decryption. This method applies the decryption algorithm using the initialized key. 

- **Error Handling:** 

The try-except block catches any exceptions that might occur during the decryption process. Common exceptions include InvalidToken if the data cannot be decrypted with the provided key. 

- **Logging and Error Display:** 

If an exception occurs, an error message is displayed using click.echo, providing information about the decryption failure. This can be useful for debugging and understanding the cause of decryption errors. 

- **Fallback Response:** 

In case of a decryption failure, the function returns an empty byte string (b''). This ensures that the calling code receives a consistent response and can handle decryption errors gracefully. 

- **Purpose of the Function:** 

The primary purpose of this function is to decrypt data using the Fernet symmetric encryption algorithm. It abstracts away the details of the decryption process and provides a convenient interface for other parts of the code to decrypt data by simply providing the encrypted data and the corresponding encryption key. 

The function includes error handling to deal with potential exceptions that might arise during the decryption process, ensuring that the application can gracefully handle and report decryption failures. This is crucial for maintaining the integrity and security of data decryption in scenarios where decryption may fail due to incorrect keys, corrupted data, or other issues. 

# 11.Download File:
```python
def download_file(bucket, file_name, local_directory, decryption_key_name):
    try:
        s3 = boto3.client('s3')

        # Ensure the local directory exists
        os.makedirs(local_directory, exist_ok=True)

        local_path = os.path.join(local_directory, file_name)

        # Download the file from S3
        s3.download_file(bucket, file_name, local_path)

        # Check if the file is encrypted (using server-side encryption)
        encryption_info = s3.head_object(Bucket=bucket, Key=file_name).get('ServerSideEncryption', None)

        if encryption_info:
            # Check if a decryption key is available
            decryption_key = encryption_keys.get(decryption_key_name)

            if decryption_key:
                try:
                    # Decrypt the downloaded file
                    with open(local_path, 'rb') as file:
                        encrypted_data = file.read()
                        decrypted_data = decrypt_data(encrypted_data, decryption_key)

                    # Write the decrypted data back to the local file
                    with open(local_path, 'wb') as file:
                        file.write(decrypted_data)

                    click.echo(f"{file_name} downloaded and decrypted to {local_path} successfully.")
                except Exception as e:
                    click.echo(f"Error decrypting data: {str(e)}")
            else:
                click.echo("Decryption key not found. File downloaded without decryption.")
        else:
            click.echo(f"{file_name} downloaded to {local_path} successfully.")

    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")
```

**Steps Explained:** 

- **S3 Client Initialization:** 

The function initializes an S3 client using boto3.client('s3') to interact with Amazon S3 services. 

- **Local Directory Creation:** 

It ensures that the local directory, where the file will be saved, exists. If not, it creates the directory using os.makedirs. 

- **Local File Path Determination:** 

It determines the full local file path by joining the local directory and the file name. 

- **File Download from S3:** 

The download_file method is used to download the file from the specified S3 bucket and save it to the local path. 

- **Check for Encryption:** 

It checks if the downloaded file is encrypted by examining the server-side encryption information retrieved using s3.head_object. 

- **Decryption Key Check:** 

If the file is encrypted, it checks if a decryption key is available in the encryption_keys dictionary using the provided decryption_key_name. 

- **Decryption Attempt:** 

If a decryption key is available, it attempts to decrypt the file using the decrypt_data function, which utilizes the Fernet symmetric encryption algorithm. 

- **Write Decrypted Data:** 

If decryption is successful, it writes the decrypted data back to the local file. 

- **Handling Decryption Failure:** 

If decryption fails, an error message is displayed using click.echo. 

- **Success Messages:** 

Depending on the outcome (whether encrypted or not), success messages are displayed indicating the success of the download operation. 

- **Error Handling:** 

The function includes error handling for various exceptions, such as NoCredentialsError, which may occur if AWS credentials are not available, and a generic Exception for other potential errors. 

- **Purpose of the Function:** 

The download_file function encapsulates the logic for securely downloading files from an S3 bucket, handling encryption and decryption as needed. It abstracts away the complexity of interacting with S3, checking for encryption, and managing decryption keys. This function is a key component in the larger application, ensuring secure and reliable file downloads from S3. 

# 12.Download From S3: 
```python

def download_from_s3(bucket):
    try:
        enable_encryption(bucket)

        s3 = session.client('s3')

        encryption_at_rest = s3.get_bucket_encryption(Bucket=bucket).get('ServerSideEncryptionConfiguration', None)
        encryption_in_transit = s3.get_bucket_policy(Bucket=bucket)['Policy']

        click.echo(f"Encryption at rest: {'enabled' if encryption_at_rest else 'disabled'}")
        click.echo(f"Encryption in transit: {'enabled' if 'aws:SecureTransport' in encryption_in_transit else 'disabled'}")

        bucket_contents = s3.list_objects_v2(Bucket=bucket).get('Contents', [])

        if not bucket_contents:
            click.echo(f"No files in the bucket '{bucket}'.")
            return

        click.echo(f"Files in the bucket '{bucket}':")
        for content in bucket_contents:
            click.echo(content['Key'])

        file_to_download = click.prompt("Enter the file name to download")
        local_directory = click.prompt("Enter the local directory to save the file")
        decryption_key_name = click.prompt("Enter the name of the encryption key: ")

        download_file(bucket, file_to_download, local_directory, decryption_key_name)

    except NoCredentialsError:
        click.echo("Credentials not available. Please set up your AWS credentials.")
    except Exception as e:
        click.echo(f"An error occurred: {str(e)}")
```

**Steps Explained:** 

- **Encryption Status Retrieval:** 

The function starts by enabling encryption using enable_encryption(bucket) to ensure the appropriate encryption settings are in place. 

- **S3 Client Initialization:** 

It initializes an S3 client using session.client('s3') to interact with Amazon S3 services. 

- **Encryption Information Retrieval:** 

Retrieves information about encryption at rest and encryption in transit for the specified S3 bucket using s3.get_bucket_encryption and s3.get_bucket_policy. 

- **Encryption Status Display:** 

Displays the encryption status (enabled or disabled) for both at rest and in transit. 

- **Bucket Contents Retrieval:** 

Retrieves the list of files (Contents) in the specified bucket using s3.list_objects_v2. 

- **Files Display:** 

Displays the list of files available in the bucket. 

- **User Input:** 

Prompts the user to enter details for the download: 

- **file_to_download:** The name of the file to download. 

- **local_directory:** The local directory to save the file. 

- **decryption_key_name:** The name of the encryption key to use for decryption. 

- **File Download:** 

Initiates the file download using the download_file function, passing the user-input details. 

- **Error Handling:** 

Includes error handling for exceptions, such as NoCredentialsError if AWS credentials are not available, and a generic Exception for other potential errors. 

- **Purpose of the Function:** 

The download_from_s3 function serves as the entry point for users to interactively initiate file downloads from an S3 bucket. It provides a user-friendly interface, checks and displays encryption status, and delegates the download process to the download_file function. This function encapsulates the user interaction and complements the overall functionality of the application for secure and controlled file retrieval from S3. 


## Secure S3 File DELETE Operations Documentation 

**1.Import Statements:** 
```python
import click
import boto3
from botocore.exceptions import NoCredentialsError, ParamValidationError
import json
```

**Explanation:** 

- **click:** A library for creating command-line interfaces (CLIs) with a decorator-based approach. 

- **boto3:** The Amazon Web Services (AWS) SDK for Python, providing an interface to interact with AWS services. 

- **NoCredentialsError:** An exception indicating that AWS credentials are not available. 

- **ParamValidationError:** An exception for validation errors in AWS service parameters. 

- **json:** A module for working with JSON data. 

# 2.AWS Session and S3 Resource Initialization: 
```python
session = boto3.Session()
s3 = session.resource('s3')
```
**Explanation:** 

- **Initializes** an AWS session and an S3 resource using boto3. 

- **session:** Represents a session with AWS services. 

- **s3:** Represents an S3 resource. 

# 3.Encryption Functions: 

```python
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
```

**Explanation:** 

- Enables encryption at rest for an S3 bucket using the AES256 algorithm. 

- s3.put_bucket_encryption: Calls the AWS API to set up bucket encryption. 

- **click.echo:** Prints messages to the command line. 

- Handles exceptions related to missing credentials or parameter validation errors.


# 4.enable_encryption_in_transit(bucket_name): 
```python
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

```
**Explanation:** 

- Enables encryption in transit for an S3 bucket by adding a bucket policy that denies insecure transport. 

- **s3.put_bucket_policy:** Calls the AWS API to set the bucket policy. 

- **json.dumps:** Converts the bucket policy dictionary to a JSON-formatted string. 

- Handles exceptions similarly to enable_encryption_at_rest.

# 5.enable_encryption(bucket_name): 

```python
def enable_encryption(bucket_name):
    click.echo(f"Enabling encryption for {bucket_name}...")
    enable_encryption_at_rest(bucket_name)
    enable_encryption_in_transit(bucket_name)
```

**Explanation:** 

- Serves as a higher-level function to enable both encryption at rest and in transit. 

- Calls enable_encryption_at_rest and enable_encryption_in_transit sequentially. 

- Prints a message indicating the initiation of the encryption process. 

# 6.delete_files_interactive(bucket, paths_to_delete): 

```python
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
```

**Explanation:**

- Provides an interactive way to delete files or folders from an S3 bucket. 

- Retrieves and prints the encryption status before deletion. 

- Uses click.confirm to ask for user confirmation before deletion. 

- Iterates through the specified paths (paths_to_delete) and deletes files or folders accordingly. 

- Handles exceptions, such as missing credentials or errors during the deletion process. 

- Prints a summary of successfully deleted files or folders. 

# 7.Main Function and CLI Interface: 
```python
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
```
**Explanation:** 

- Defines a CLI interface using click for the main functionality. 

- Options include --bucket for specifying the S3 bucket and --command for selecting the operation. 

- The main function is the entry point for command execution. 

- Calls enable_encryption to ensure encryption settings are in place. 

- Executes the specified command, in this case, delete_files_interactive. 

- Displays a message for unsupported commands. 

**Summary:** 

The provided code is a script for interacting with an Amazon S3 bucket, focusing on encryption and interactive file deletion. It is structured to provide modularity, readability, and an interactive command-line interface. Users can execute commands like enabling encryption, deleting files or folders interactively, and more. The script handles various scenarios, including encryption status display, user confirmation, and error handling. The modular design allows for easy extension with additional commands or functionality.


# Secure S3 File LOG Operations Documentation

## Table of Contents

### Imports

### Function Definitions

1. enable_encryption_at_rest Function
2. enable_encryption_in_transit Function
3. view_s3_bucket_logs Function

### Function Implementations

1. enable_encryption_at_rest Function Implementation
2. enable_encryption_in_transit Function Implementation
3. view_s3_bucket_logs Function Implementation

### Main Block

# 1.Imports

```python
click
boto3
json
NoCredentialsError, ParamValidationError from botocore.exceptions
tabulate
```

# Explanation: 

- click: A Python package for creating command-line interfaces (CLIs). 

- boto3: AWS SDK for Python. Allows interaction with AWS services. 

- json: Standard Python library for working with JSON data. 

- NoCredentialsError, ParamValidationError: Exceptions from botocore for handling AWS credential and parameter validation errors. 

- tabulate: A library for creating formatted tables in the console.

# 2.Function Definitions 
```python
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

```
# Explanation: 

**Three main functions:** 

- enable_encryption_at_rest: Enables encryption at rest for an S3 bucket. 

- enable_encryption_in_transit: Enables encryption in transit for an S3 bucket. 

- view_s3_bucket_logs: Views activity logs (file names, sizes, and upload timings) of an S3 bucket.

# 3.Enable_encryption_at_rest Function Implementation 

```python
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

```

**Explanation:** 

- Create S3 client: Initiates an S3 client. 

- Configure encryption: Configures server-side encryption for the specified bucket. 

- Display message: Notifies about successful encryption at rest. 

- Exception handling: Catches errors related to credentials and parameter validation.

# 4.Enable_encryption_in_transit Function Implementation 
```python
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
```
**Explanation:** 

- Create S3 client: Initializes an S3 client. 

- Define bucket policy: Specifies a bucket policy to deny unsecured transport. 

- Apply policy: Associates the policy with the specified bucket. 

- Display message: Notifies about successful encryption in transit. 

- Exception handling: Handles errors related to credentials and parameter validation.

# 5.view_s3_bucket_logs Function Implementation 
```python
try:
    enable_encryption_at_rest(bucket_name)
    enable_encryption_in_transit(bucket_name)
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    table_data = []
    for index, obj in enumerate(bucket.objects.all(), start=1):
        size_mb = obj.size / (1024 ** 2)
        timing = obj.last_modified.strftime("%Y-%m-%d %H:%M:%S")
        table_data.append([str(index), obj.key, f"{size_mb:.2f} MB", timing])
    headers = ["S.No", "Name", "Size", "Timing of Uploading"]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
    click.echo(f"S3 bucket activity logs for '{bucket_name}':")
except Exception as e:
    click.echo(f"Error retrieving S3 bucket activity logs: {str(e)}")
```
**Explanation:** 

- Enable encryption: Calls functions to enable encryption at rest and in transit. 

- Create S3 resource: Initializes an S3 resource using the provided bucket name. 

- Collect data for the table: Iterates over the bucket's objects and collects information. 

- Display table: Uses tabulate to format and display the data in a table.

- Exception handling: Catches errors related to retrieving S3 bucket activity logs.

# Secure S3 File Listing Documentation

Table of Contents

- Introduction

- Prerequisites

- Installation

- Configuration

  **Introduction** 

This script facilitates the secure listing of contents within an Amazon S3 bucket. It employs the AWS SDK for Python (boto3) and integrates with the click library to create a command-line interface (CLI) for interaction.

**Prerequisites** 

- Python installed 

- AWS credentials properly configured 

**Installation** 

The script relies on the following Python packages: 

- click 

- boto3 

- tabulate 

- Listing Mechanism

Main Block

**1.You can install these dependencies using the following command:**

```python
pip install click boto3 tabulate
```

**Configuration** 

Ensure that your AWS credentials are configured on your system. This typically involves setting up the AWS access key ID and secret access key. If not already done, you can configure your credentials using the AWS Command Line Interface (CLI) or by exporting environment variables. 

# 2.Listing Mechanism

The script defines a function list_folder_contents that lists the contents of an S3 bucket with serial numbers for easy reference. It utilizes the boto3 library for S3 interactions and click for command-line interface features. 

```python
def list_folder_contents(bucket, region="eu-north-1"): 

    # ...
```
**Function Explanation:** 

list_folder_contents Function: Lists the contents of an S3 bucket with serial numbers. 

**Parameters:** 

- bucket: The name of the S3 bucket to list. 

- region: The AWS region in which the bucket is located (default is "eu-north-1").

# 3.Function Explanation: 
```python
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
 ```

**Explanation:** 

- List Contents: Uses the boto3 client to list the contents of the specified S3 bucket. 

- Table Data Collection: Iterates over the bucket's objects, collecting information like the file name and assigning serial numbers. 

- Display Table: Uses tabulate to format and display the data in a grid table. 

- Exception Handling: Catches errors related to credentials and general exceptions during execution.

  **Conclusion** 

This script serves as a simple yet effective tool for securely listing contents within an S3 bucket. The provided CLI and tabular presentation enhance user experience and readability. 
