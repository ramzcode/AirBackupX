from flask import Flask, request, jsonify
from cryptography.fernet import Fernet, InvalidToken
import mysql.connector
import os

app = Flask(__name__)

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

# Create the 'passwords' table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS passwords (
        username VARCHAR(255),
        device VARCHAR(255) UNIQUE,
        encrypted_password BLOB
    )
''')
conn.commit()

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

# API endpoint to create credentials
@app.route('/api/create', methods=['POST'])
def create_credentials():
    data = request.json
    
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    username = data.get('username')
    device = data.get('device')
    password = data.get('password')
    
    if not username or not device or not password:
        return jsonify({'error': 'Please provide username, device, and password'}), 400
    
    # Check if the device name already exists
    cursor.execute('SELECT device FROM passwords WHERE device = %s', (device,))
    result = cursor.fetchone()
    if result:
        return jsonify({'error': f"Device '{device}' already exists. Please choose a different device name."}), 400
    else:
        encrypted_password = encrypt_password(password)
        try:
            cursor.execute('INSERT INTO passwords (username, device, encrypted_password) VALUES (%s, %s, %s)',
                           (username, device, encrypted_password))
            conn.commit()
            return jsonify({'message': 'Credentials saved successfully'}), 201
        except mysql.connector.IntegrityError as e:
            if e.errno == 1062:
                return jsonify({'error': f"Device '{device}' already exists. Please choose a different device name."}), 400
            else:
                return jsonify({'error': f"An error occurred: {e}"}), 500

# API endpoint to retrieve credentials by device name
@app.route('/api/retrieve/<device>', methods=['GET'])
def retrieve_credentials(device):
    cursor.execute('SELECT username, encrypted_password FROM passwords WHERE device = %s', (device,))
    result = cursor.fetchone()
    if result:
        username, encrypted_password = result
        decrypted_password = decrypt_password(encrypted_password)
        return jsonify({'username': username, 'password': decrypted_password}), 200
    else:
        return jsonify({'error': f"No credentials found for device {device}"}), 404

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=3031)

