import mysql.connector
from cryptography.fernet import Fernet, InvalidToken
import os
import logging
import time
import importlib
import sys

sys.path.append("/Users/ram/Downloads/AirBackupX/scripts")

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

# Create a custom logger
logger = logging.getLogger('custom_runner')
logger.setLevel(logging.INFO)

# Create a formatter with the desired format
formatter = logging.Formatter('%(site)s:%(status)s')

# Create a file handler and set the formatter for the handler
file_handler = logging.FileHandler('/Users/ram/Downloads/AirBackupX/runner.log')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Establish a connection to the MySQL database
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='hack',
    database='passwords_db'
)

# Retrieve the devices
cursor = connection.cursor(dictionary=True)
group_name = 'GNS3-Local'
query = ("SELECT * FROM passwords WHERE group_name = %s")
values = (group_name,)
cursor.execute(query, values)
devices = cursor.fetchall()



logger.info('Job started', extra={'site': group_name, 'status': 'RunningFromLogger'})

# Process devices
for device in devices:
    username = device['username']
    device_name = device['device']
    encrypted_password = device['encrypted_password']
    decrypted_password = decrypt_password(encrypted_password)  # Decrypt the password
    device_type = device['type']

    module_name = f"module_{device_type.lower()}"
    try:
        module = __import__(module_name)   
        time.sleep(8)
        module.process_device(device_name, username, decrypted_password, group_name, device_type)
    except ImportError:
        print(f"Module for device type '{device_type}' not found.")
        logger.info('Job completed', extra={'site': group_name, 'status': 'FatalFromLogger'})

# Example log messages using the custom logger
logger.info('Job completed', extra={'site': group_name, 'status': 'CompletedFromLogger'})

# Close the cursor and connection
connection.commit()
cursor.close()
connection.close()