import mysql.connector
from cryptography.fernet import Fernet, InvalidToken
import os

# Generate a Fernet key
# Function to generate or load the encryption key
def get_or_generate_key():
    key_file = 'encryption_key.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as file:
            key = file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as file:
            file.write(key)
    return key

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
group_name = 'MANA1'

# Query to retrieve devices based on group name
query = ("SELECT * FROM passwords WHERE group_name = %s")
values = (group_name,)

# Execute the query
cursor.execute(query, values)

# Retrieve the devices
devices = cursor.fetchall()

# Process devices
for device in devices:
    username = device['username']
    device_name = device['device']
    encrypted_password = device['encrypted_password']
    decrypted_password = decrypt_password(encrypted_password)  # Decrypt the password
    device_type = device['type']

    # Process devices based on their type
    if device_type == 'asdad':
        # Process devices of type 'asdad'
        print(f"Processing device {device_name} of type 'asdad' with username {username} and decrypted password {decrypted_password}")
    elif device_type == 'IOS':
        # Process devices of type 'IOS'
        print(f"Processing device {device_name} of type 'IOS' with username {username} and decrypted password {decrypted_password}")

# Close the cursor and connection
cursor.close()
connection.close()

