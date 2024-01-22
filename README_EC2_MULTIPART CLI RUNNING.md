# Running Multi-Part S3 on Ec2 linux CLI.

**To run your Python code on an EC2 instance running Linux, you can follow these general steps. This assumes that you have already set up an EC2 instance and have the necessary permissions and access to the instance.**

# 1.Transfer Your Code to EC2:
- SSH Key Pair: Ensure that you are using the correct SSH private key corresponding to the public key associated with the EC2 instance.

- Correct Username: Make sure you are using the correct username for the EC2 instance. The default username for Amazon Linux is usually ec2-user, and for other distributions, it might be ubuntu, centos, or something else depending on the AMI.

- Key Permissions: Check the permissions of your private key file (id_rsa or similar). It should not be publicly viewable. You can fix the permissions using the following command:
```python
chmod 400 /path/to/your/private/key
```
- Security Group: Ensure that the security group associated with your EC2 instance allows SSH traffic (port 22) from your local machine's IP address.

- Firewall: If you have a firewall running on your local machine, ensure that it allows outgoing SSH connections.
- Use a tool like scp (secure copy) or rsync to transfer your Python script or code directory to the EC2 instance. Replace your_key.pem and your_ec2_public_ip with your actual key file and EC2 instance public IP.
```python
scp -i your_key.pem your_script.py ec2-user@your_ec2_public_ip:/path/to/remote/directory
```
Replace the following placeholders:

- /path/to/your/local/file: Path to the file on your local machine.
- username: Your EC2 instance username.
- ec2-instance-ip: The public IP address or DNS of your EC2 instance.
- /path/on/ec2: The destination path on your EC2 instance.
**Example**
```python
  scp /path/to/my/code.py ec2-user@1.2.3.4:/home/ec2-user/multipart_upload
```
# 2.Connect to EC2:

```python
ssh -i your_key.pem ec2-user@your_ec2_public_ip
```
- Connect to your EC2 instance using SSH.

**connect to your EC2 instance using SSH, follow these steps. Please note that the specific details may vary depending on your operating system and the configuration of your EC2 instance.**

**1.Prerequisites:**
- Public IP or DNS of your EC2 instance: You should know the public IP address or the DNS name associated with your EC2 instance.

- SSH Key Pair: You should have the private key corresponding to the key pair used when launching the EC2 instance. If you don't have the private key, you may need to create a new key pair or use an existing one.

**Steps:**
**For Linux/Mac:**
**Open a terminal on your local machine.**

- Use the ssh command to connect to your EC2 instance. Replace your-private-key.pem with the path to your private key file and your-instance-ip with the public IP or DNS of your EC2 instance.
```python
ssh -i /path/to/your-private-key.pem ec2-user@your-instance-ip
```
- If you are using a different username (e.g., ubuntu for Ubuntu instances), replace ec2-user with the appropriate username.

- If prompted, type "yes" to confirm the connection.

**For Windows:**
- Use an SSH client. If you are using Windows 10 or later, you can use the built-in OpenSSH client.

 **Open PowerShell or Command Prompt.**

- Use the ssh command. Replace your-private-key.pem with the path to your private key file and your-instance-ip with the public IP or DNS of your EC2 instance.
```python
ssh -i C:\path\to\your-private-key.pem ec2-user@your-instance-ip
```
- If you are using a different username (e.g., ubuntu for Ubuntu instances), replace ec2-user with the appropriate username.

- If prompted, type "yes" to confirm the connection.

**Troubleshooting Tips:**
- If you encounter permission issues with the private key file, make sure it is not publicly accessible. On Linux/Mac, you can set the correct permissions using chmod 400 /path/to/your-private-key.pem.

- Ensure that your EC2 instance's security group allows SSH traffic (port 22) from your local machine.

- Double-check the EC2 instance's public IP or DNS and the private key path.

- If you're using a different SSH client on Windows, follow the specific instructions for that client.
```python
ssh -i your_key.pem ec2-user@your_ec2_public_ip
```
# 3.Run Your Python Script:
```python
cd /path/to/remote/directory
```
- Navigate to the directory where your Python script is located.

# 4.Keep the Process Running:

- If you want your script to keep running after you disconnect from the SSH session, consider using tools like tmux or nohup. For example:
```python
  nohup python your_script.py &
```
# Note
Remember to manage your dependencies, environment, and execution based on your specific requirements and use case. Additionally, ensure that your EC2 security groups allow SSH access (port 22) and any other ports necessary for your application. Adjust the security group settings as needed.
