from cryptography.fernet import Fernet
import sqlite3
import os

# Generate a secret key for encryption (you should store this securely)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Function to encrypt a password
def encrypt_password(password):
    encrypted_password = cipher_suite.encrypt(password.encode())
    return encrypted_password

# Function to decrypt a password
def decrypt_password(encrypted_password):
    decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
    return decrypted_password

# Check if the database file exists; if not, create it
db_file = 'passwords.db'
if not os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create the 'passwords' table with 'device' as a unique field
    cursor.execute('''
        CREATE TABLE passwords (
            username TEXT,
            device TEXT UNIQUE,
            encrypted_password BLOB
        )
    ''')
    conn.commit()
else:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

# Function to save an encrypted password and device to the database
def save_password(username, device, password):
    encrypted_password = encrypt_password(password)
    cursor.execute('INSERT OR REPLACE INTO passwords (username, device, encrypted_password) VALUES (?, ?, ?)',
                   (username, device, encrypted_password))
    conn.commit()

# Function to retrieve and decrypt a password by device name
def get_password(device):
    cursor.execute('SELECT username, encrypted_password FROM passwords WHERE device = ?', (device,))
    result = cursor.fetchone()
    if result:
        username, encrypted_password = result
        decrypted_password = decrypt_password(encrypted_password)
        return username, decrypted_password
    else:
        return None, None

# Create or retrieve credentials by device name
while True:
    print("1. Create credentials")
    print("2. Retrieve credentials by device")
    print("3. Exit")
    choice = input("Enter your choice (1/2/3): ")

    if choice == '1':
        username = input("Enter username: ")
        device = input("Enter device name: ")
        password = input("Enter password: ")
        save_password(username, device, password)
        print("Credentials saved successfully!\n")
    elif choice == '2':
        device = input("Enter device name: ")
        username, retrieved_password = get_password(device)
        if username and retrieved_password:
            print(f"Username: {username}")
            print(f"Decrypted Password for {device}: {retrieved_password}\n")
        else:
            print(f"No credentials found for device {device}.\n")
    elif choice == '3':
        break
    else:
        print("Invalid choice. Please enter 1, 2, or 3.\n")

# Close the database connection when done
conn.close()

