from flask import Flask, render_template, request, redirect, url_for, flash
from cryptography.fernet import Fernet, InvalidToken
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong, random value

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

# Function to list available device names
def list_devices():
    cursor.execute('SELECT device FROM passwords')
    results = cursor.fetchall()
    devices = [result[0] for result in results]
    return devices

# Define routes and views
@app.route('/')
def index():
    devices = list_devices()
    return render_template('index.html', devices=devices)
@app.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        username = request.form['username']
        device = request.form['device']
        password = request.form['password']

        # Check if any form field is empty
        if not username or not device or not password:
            flash("Please fill in all fields.", 'error')
        else:
            # Check if the device name already exists
            cursor.execute('SELECT device FROM passwords WHERE device = %s', (device,))
            result = cursor.fetchone()
            if result:
                flash(f"Device '{device}' already exists. Please choose a different device name.", 'error')
            else:
                encrypted_password = encrypt_password(password)
                try:
                    cursor.execute('INSERT INTO passwords (username, device, encrypted_password) VALUES (%s, %s, %s)',
                                   (username, device, encrypted_password))
                    conn.commit()
                    flash("Credentials saved successfully!", 'success')
                except mysql.connector.IntegrityError as e:
                    if e.errno == 1062:
                        flash(f"Device '{device}' already exists. Please choose a different device name.", 'error')
                    else:
                        flash(f"An error occurred: {e}", 'error')

    return redirect(url_for('index'))

@app.route('/retrieve', methods=['POST', 'GET'])
def retrieve():
    if request.method == 'POST':
        device = request.form['device']
        
        # Check if the device name is empty
        if not device:
            flash("Please enter a device name.", 'error')
        else:
            cursor.execute('SELECT username, encrypted_password FROM passwords WHERE device = %s', (device,))
            result = cursor.fetchone()
            if result:
                username, encrypted_password = result
                decrypted_password = decrypt_password(encrypted_password)
                return render_template('retrieve.html', username=username, password=decrypted_password)
            else:
                flash(f"No credentials found for device {device}.", 'error')
    
    return render_template('retrieve.html', username=None, password=None)

# Function to edit credentials by device name
@app.route('/edit/<device>', methods=['POST', 'GET'])
def edit(device):
    cursor.execute('SELECT username FROM passwords WHERE device = %s', (device,))
    result = cursor.fetchone()
    
    if result:
        old_username = result[0]

        if request.method == 'POST':
            new_username = request.form['new_username']
            new_password = request.form['new_password']

            if not new_username or not new_password:
                flash("Please fill in all fields.", 'error')
            else:
                encrypted_password = encrypt_password(new_password)
                try:
                    cursor.execute('UPDATE passwords SET username = %s, encrypted_password = %s WHERE device = %s',
                                   (new_username, encrypted_password, device))
                    conn.commit()
                    flash("Credentials updated successfully!", 'success')
                except Exception as e:
                    flash(f"An error occurred: {e}", 'error')
    else:
        flash(f"No credentials found for device {device}.", 'error')
        return redirect(url_for('index'))

    return render_template('edit.html', device=device, old_username=old_username)


# Function to delete credentials by device name
@app.route('/delete/<device>', methods=['GET'])
def delete(device):
    try:
        cursor.execute('DELETE FROM passwords WHERE device = %s', (device,))
        conn.commit()
        flash(f"Device '{device}' deleted successfully!", 'success')
    except Exception as e:
        flash(f"An error occurred: {e}", 'error')

    return redirect(url_for('index'))


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')
