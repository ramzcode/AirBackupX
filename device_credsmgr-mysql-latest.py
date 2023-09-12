from cryptography.fernet import Fernet, InvalidToken
import mysql.connector
import os

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

# Connect to MySQL/MariaDB database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'hack',
    'database': 'passwords_db'
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Function to encrypt a password
def encrypt_password(password):
    encrypted_password = cipher_suite.encrypt(password.encode())
    return encrypted_password

# Function to decrypt a password
def decrypt_password(encrypted_password):
    try:
        decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
        return decrypted_password
    except InvalidToken:
        return "Invalid token (possibly corrupted or tampered data)"

# Create the 'passwords' table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS passwords (
        username VARCHAR(255),
        device VARCHAR(255) UNIQUE,
        encrypted_password BLOB
    )
''')
conn.commit()

# Function to save an encrypted password and device to the database
def save_password(username, device, password):
    encrypted_password = encrypt_password(password)
    try:
        cursor.execute('INSERT INTO passwords (username, device, encrypted_password) VALUES (%s, %s, %s)',
                       (username, device, encrypted_password))
        conn.commit()
        print("Credentials saved successfully!\n")
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # Check for duplicate entry error
            print(f"Device '{device}' already exists. Please choose a different device name.\n")
        else:
            print(f"An error occurred: {e}\n")

# Function to retrieve and decrypt a password by device name
def get_password(device):
    cursor.execute('SELECT username, encrypted_password FROM passwords WHERE device = %s', (device,))
    result = cursor.fetchone()
    if result:
        username, encrypted_password = result
        decrypted_password = decrypt_password(encrypted_password)
        return username, decrypted_password
    else:
        return None, None

# Function to delete a device by device name
def delete_device(device):
    cursor.execute('SELECT device FROM passwords WHERE device = %s', (device,))
    result = cursor.fetchone()
    if result:
        cursor.execute('DELETE FROM passwords WHERE device = %s', (device,))
        conn.commit()
        print(f"Device '{device}' deleted successfully!\n")
    else:
        print(f"Device '{device}' not found. Cannot delete.\n")


# Function to edit the password for a device
def edit_device(device):
    username, _ = get_password(device)
    if username:
        new_device = input(f"Enter a new device name (or press Enter to keep '{device}'): ")
        if new_device:
            if new_device != device:
                # Check if the new device name already exists
                cursor.execute('SELECT device FROM passwords WHERE device = %s', (new_device,))
                result = cursor.fetchone()
                if result:
                    print(f"Device '{new_device}' already exists. Please choose a different device name.")
                    return
            new_password = input(f"Enter a new password for {device}: ")
            delete_device(device)  # Delete the existing entry
            save_password(username, new_device, new_password)  # Save with the new device name
            print(f"Device name updated to '{new_device}'. Password updated successfully!\n")
        else:
            new_password = input(f"Enter a new password for {device}: ")
            save_password(username, device, new_password)  # Keep the same device name
            print(f"Password for '{device}' updated successfully!\n")
    else:
        print(f"Device '{device}' not found. Cannot edit.\n")

# Function to list available device names
def list_devices():
    cursor.execute('SELECT device FROM passwords')
    results = cursor.fetchall()
    if results:
        print("Available device names:")
        for result in results:
            print(result[0])
    else:
        print("No device names found in the database.")

# Create, retrieve, edit, or delete credentials by device name
while True:
    print("1. Create credentials")
    print("2. Retrieve credentials by device")
    print("3. Edit credentials by device")
    print("4. Delete credentials by device")
    print("5. List available device names")
    print("6. Exit")
    choice = input("Enter your choice (1/2/3/4/5/6): ")

    if choice == '1':
        username = input("Enter username: ")
        device = input("Enter device name: ")
        password = input("Enter password: ")
        save_password(username, device, password)
    elif choice == '2':
        device = input("Enter device name: ")
        username, retrieved_password = get_password(device)
        if username and retrieved_password:
            print(f"Username: {username}")
            print(f"Decrypted Password for {device}: {retrieved_password}\n")
        else:
            print(f"No credentials found for device {device}.\n")
    elif choice == '3':
        device = input("Enter device name: ")
        edit_device(device)
    elif choice == '4':
        device = input("Enter device name: ")
        delete_device(device)
    elif choice == '5':
        list_devices()
    elif choice == '6':
        break
    else:
        print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.\n")

# Close the database connection when done
conn.close()
