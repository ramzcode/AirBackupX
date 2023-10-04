import mysql.connector
from cryptography.fernet import Fernet, InvalidToken
import os
import logging
import time
import importlib
import sys
import module_ios
sys.path.append("/Users/ram/Downloads/AirBackupX/scripts")

logging.basicConfig(filename='runner.log', level=logging.INFO, format='%(site)s:%(status)s')

# Function to load the encryption key
def get_or_generate_key():
    key_file = 'encryption_key.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as file:
            key = file.read()
            return key
    else:
        print('DecryptionKey Not Found')
        raise FileNotFoundError('Decryption key file not found. Please save the key and save it in "encryption_key.key".')

# Initialize Fernet cipher with the key
encryption_key = get_or_generate_key()
cipher_suite = Fernet(encryption_key)

# Function to decrypt a password
def decrypt_password(encrypted_password):
    try:
        decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
        return decrypted_password
    except InvalidToken:
        return "Invalid token (possibly corrupted or tampered data)"


# Establish a connection to the MySQL database
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='hack',
    database='passwords_db'
)

# Create a cursor object to interact with the database
cursor = connection.cursor(dictionary=True)

# Specify the group you want to filter
group_name = 'GNS3-Local'

# Query to retrieve devices based on group name
query = ("SELECT * FROM passwords WHERE group_name = %s")
values = (group_name,)

# Execute the query
cursor.execute(query, values)

# Retrieve the devices
devices = cursor.fetchall()

logging.info('Job started', extra={'site': group_name, 'status': 'Running'})

# Process devices
for device in devices:
    username = device['username']
    device_name = device['device']
    encrypted_password = device['encrypted_password']
    decrypted_password = decrypt_password(encrypted_password)  # Decrypt the password
    device_type = device['type']

    # Process devices based on their type

    # # Process devices based on their type
    # if device_type == 'ASA':
    #     # Process devices of type 'ASA'
    #     print(f"Processing device {device_name} of type 'ASA' with username {username} and decrypted password {decrypted_password}")
    #     logging.info('Job started', extra={'site': group_name, 'status': 'running'})
    #     time.sleep(8)
    #     logging.info('Job completed', extra={'site': group_name, 'status': 'completed'})
    #     time.sleep(8)
    # elif device_type == 'IOS':
    #     # Process devices of type 'IOS'
    #     print(f"Processing device {device_name} of type 'IOS' with username {username} and decrypted password {decrypted_password}")
    #     logging.info('Job started', extra={'site': group_name, 'status': 'running'})
    #     time.sleep(8)
    #     logging.info('Job completed', extra={'site': group_name, 'status': 'completed'})
    #     time.sleep(8)

    module_name = f"module_{device_type.lower()}"
    #print(f"Importing module: {module_name}")
    try:
        module = __import__(module_name)   
        time.sleep(8)
        module.process_device(device_name, username, decrypted_password, group_name)
    except ImportError:
        print(f"Module for device type '{device_type}' not found.")

logging.info('Job started', extra={'site': group_name, 'status': 'Completed'})

# Close the cursor and connection
cursor.close()
connection.close()