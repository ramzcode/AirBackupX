from cryptography.fernet import Fernet
import sqlite3

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

# Create or connect to an SQLite database
conn = sqlite3.connect('passwords.db')
cursor = conn.cursor()

# Create a table to store encrypted passwords
cursor.execute('''
    CREATE TABLE IF NOT EXISTS passwords (
        username TEXT PRIMARY KEY,
        encrypted_password BLOB
    )
''')
conn.commit()

# Function to save an encrypted password to the database
def save_password(username, password):
    encrypted_password = encrypt_password(password)
    cursor.execute('INSERT OR REPLACE INTO passwords (username, encrypted_password) VALUES (?, ?)',
                   (username, encrypted_password))
    conn.commit()

# Function to retrieve and decrypt a password from the database
def get_password(username):
    cursor.execute('SELECT encrypted_password FROM passwords WHERE username = ?', (username,))
    result = cursor.fetchone()
    if result:
        encrypted_password = result[0]
        decrypted_password = decrypt_password(encrypted_password)
        return decrypted_password
    else:
        return None

# Create or retrieve credentials
while True:
    print("1. Create credentials")
    print("2. Retrieve credentials")
    print("3. Exit")
    choice = input("Enter your choice (1/2/3): ")

    if choice == '1':
        username = input("Enter username: ")
        password = input("Enter password: ")
        save_password(username, password)
        print("Credentials saved successfully!\n")
    elif choice == '2':
        username = input("Enter username: ")
        retrieved_password = get_password(username)
        if retrieved_password:
            print(f"Decrypted Password for {username}: {retrieved_password}\n")
        else:
            print(f"Password for {username} not found in the database.\n")
    elif choice == '3':
        break
    else:
        print("Invalid choice. Please enter 1, 2, or 3.\n")

# Close the database connection when done
conn.close()

