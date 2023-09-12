from cryptography.fernet import Fernet
import mysql.connector

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

# Connect to MySQL/MariaDB database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'hack',
    'database': 'passwords_db'
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

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

