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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS types (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE
    )
''')


#cursor.execute('''
#    ALTER TABLE passwords
#    ADD COLUMN type VARCHAR(255)
#''')

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

# Function to list available groups
def list_groups():
    cursor.execute('SELECT name FROM groups')
    results = cursor.fetchall()
    groups = [result[0] for result in results]
    return groups

# Function to list available types
def list_types():
    cursor.execute('SELECT name FROM types')
    results = cursor.fetchall()
    types = [result[0] for result in results]
    return types


# Define routes and views
@app.route('/')
def index():
    devices = list_devices()
    groups = list_groups()
    types = list_types()
    return render_template('index.html', devices=devices, groups=groups, types=types)

@app.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        username = request.form['username']
        device = request.form['device']
        password = request.form['password']
        selected_group = request.form['group']
        selected_type = request.form['type']

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
                    cursor.execute('INSERT INTO passwords (username, device, encrypted_password, group_name, type ) VALUES (%s, %s, %s, %s, %s)',
                                   (username, device, encrypted_password, selected_group, selected_type))
                    conn.commit()
                    flash("Device created successfully!", 'success')
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

@app.route('/create_group', methods=['POST'])
def create_group():
    if request.method == 'POST':
        group_name = request.form['group_name']
        if group_name:
            try:
                # Check if the group already exists
                cursor.execute('SELECT id FROM groups WHERE name = %s', (group_name,))
                existing_group = cursor.fetchone()
                if existing_group:
                    flash(f"Group '{group_name}' already exists. Please choose a different group name.", 'error')
                else:
                    cursor.execute('INSERT INTO groups (name) VALUES (%s)', (group_name,))
                    conn.commit()
                    flash(f"Group '{group_name}' created successfully!", 'success')
            except Exception as e:
                flash(f"An error occurred: {e}", 'error')
        else:
            flash("Please enter a group name.", 'error')

    return redirect(url_for('index'))

@app.route('/delete_group', methods=['GET', 'POST'])
def delete_group():
    groups = list_groups()
    
    if request.method == 'POST':
        # Handle group deletion here
        group_to_delete = request.form.get('delete_group')
        if group_to_delete:
            # Add code to delete the selected group from the database
            try:
                cursor.execute('DELETE FROM groups WHERE name = %s', (group_to_delete,))
                conn.commit()
                flash(f"Group '{group_to_delete}' deleted successfully!", 'success')
            except Exception as e:
                flash(f"An error occurred: {e}", 'error')
        else:
            flash("Please select a group to delete.", 'error')

    return redirect(url_for('index'))

@app.route('/update_device_group/<device>', methods=['POST'])
def update_device_group(device):
    if request.method == 'POST':
        group_id = request.form['group_id']
        if group_id:
            try:
                cursor.execute('UPDATE devices SET group_id = %s WHERE name = %s', (group_id, device))
                conn.commit()
                flash(f"Group updated successfully for device '{device}'!", 'success')
            except Exception as e:
                flash(f"An error occurred: {e}", 'error')
        else:
            flash("Please select a group.", 'error')
    return redirect(url_for('index'))


@app.route('/create_type', methods=['POST'])
def create_type():
    if request.method == 'POST':
        type_name = request.form['type_name']
        if type_name:
            try:
                # Check if the group already exists
                cursor.execute('SELECT id FROM types WHERE name = %s', (type_name,))
                existing_type = cursor.fetchone()
                if existing_type:
                    flash(f"type '{type_name}' already exists. Please choose a different type name.", 'error')
                else:
                    cursor.execute('INSERT INTO types (name) VALUES (%s)', (type_name,))
                    conn.commit()
                    flash(f"type '{type_name}' created successfully!", 'success')
            except Exception as e:
                flash(f"An error occurred: {e}", 'error')
        else:
            flash("Please enter a type name.", 'error')

    return redirect(url_for('index'))

@app.route('/delete_type', methods=['GET', 'POST'])
def delete_type():
    types = list_types()
    
    if request.method == 'POST':
        # Handle group deletion here
        type_to_delete = request.form.get('delete_type')
        if type_to_delete:
            # Add code to delete the selected group from the database
            try:
                cursor.execute('DELETE FROM types WHERE name = %s', (type_to_delete,))
                conn.commit()
                flash(f"Type '{type_to_delete}' deleted successfully!", 'success')
            except Exception as e:
                flash(f"An error occurred: {e}", 'error')
        else:
            flash("Please select a type to delete.", 'error')

    return redirect(url_for('index'))

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=3030)
