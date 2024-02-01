import mysql.connector
from flask import request, redirect, flash, url_for, render_template
from app import app
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet, InvalidToken
import smtplib
from email.message import EmailMessage
import secrets
from config.config import CONFIG
import json

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


# Encrypt the password
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

def test_db_connection(db_ip, db_port, db_username, db_password):
    try:
        connection = mysql.connector.connect(
            host=db_ip,
            port=db_port,
            user=db_username,
            password=db_password,
        )

        if connection.is_connected():
            # Connection established, return True
            connection.close()
            return True
    except Exception as e:
        print("Error:", e)
    
    # Connection failed, return False
    return False


def setup1():
    if request.method == 'POST':
        db_ip = request.form['db_ip']
        db_port = request.form['db_port']
        db_username = request.form['db_username']
        db_password = request.form['db_password']

        # Test the database connection
        if test_db_connection(db_ip, db_port, db_username, db_password):
            # Connect to MySQL/MariaDB database
            dbinit_config = {
                'host': db_ip,
                'user': db_username,
                'port': db_port,
                'password': db_password,
            }
            
            conn = mysql.connector.connect(**dbinit_config)
            cursor = conn.cursor()

            cursor.execute("CREATE DATABASE IF NOT EXISTS airbackupx")
            conn.commit()

            db_config = {
                'host': db_ip,
                'user': db_username,
                'port': db_port,
                'password': db_password,
                'database': 'airbackupx'
            }

            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            # Create the 'passwords' table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    username VARCHAR(255),
                    device VARCHAR(255) UNIQUE,
                    encrypted_password BLOB,
                    group_name varchar(255),
                    type varchar(255)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS smtp_config (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    smtp_server VARCHAR(255),
                    smtp_port INT,
                    username VARCHAR(255) UNIQUE,
                    encrypted_password BLOB
            );
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
            
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    emailID VARCHAR(255) NOT NULL,
                    role VARCHAR(255) NOT NULL,
                    totp_secret VARCHAR(255) NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cron_jobs (
                    job_id VARCHAR(255) PRIMARY KEY,
                    site_name VARCHAR(255),
                    script_path VARCHAR(255),
                    minute VARCHAR(10),
                    hour VARCHAR(10),
                    day VARCHAR(10),
                    month VARCHAR(10),
                    day_of_week VARCHAR(10)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backup_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    backup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    device_name VARCHAR(255) NOT NULL,
                    site_name VARCHAR(255) NOT NULL,
                    type VARCHAR(255) NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    exit_status ENUM('failed', 'succeeded') NOT NULL,
                    file_name VARCHAR(255) NOT NULL
                )
            ''')
            
            conn.commit()
            #conn.close()

            # Read the existing Python configuration file
            with open('config/config.py', 'r') as py_file:
                python_code = py_file.read()

            # Extract CONFIG dictionary from the Python code
            exec(python_code, globals())
            config_data = globals().get('CONFIG', {})
            # Update the nested configuration
            config_data['Database']['host'] = db_ip
            config_data['Database']['port'] = db_port
            config_data['Database']['username'] = db_username
            config_data['Database']['password'] = db_password
            config_data['Database']['database'] = 'airbackupx'
        
            # Convert the updated dictionary to JSON format
            json_config = json.dumps(config_data, indent=4)
        
            # Write the updated JSON data back to the Python configuration file
            with open('config/config.py', 'w') as py_file:
                py_file.write(f'CONFIG = {json_config}')
        
            # Database connection successful, proceed to the next page
            flash("DB setup completed", 'success')
            return redirect('/setup2')
            
        else:
            # Database connection failed, show an error message
            error_message = "Failed to connect to the database. Please check your credentials."
            return render_template('setup.html', error_message=error_message)

    return render_template('setup1.html')

def setup2():
    if request.method == 'POST':
        # Key Management
        flask_secret_key = secrets.token_hex(24)  # Auto-generate session secret
        flask_session_prefix = 'airbackupx'

        # Admin Password
        admin_password = request.form['admin_password']
        admin_email = request.form['admin_email']

        # Fernet Key Management
        fernet_key = request.form['fernet_key']
        print('Encrypt Key Generated and saved')
#        if len(fernet_key) < 24:
#            return render_template('setup2.html', error_message='Encryption key must be at least 24 characters long.')
#
#        # Save Fernet Key to a file (for example, fernet_key.txt)
#        with open('encryption_key.key', 'w') as key_file:
#            key_file.write(fernet_key)

        # Backup Path Validation
        backup_path = request.form['backup_path']
        if not os.path.exists(backup_path):
            return render_template('setup2.html', error_message='Backup path does not exist.')
        elif not os.access(backup_path, os.W_OK):
            return render_template('setup2.html', error_message='Airbackupx user does not have write permission in the provided path.')
        

        # Database connection configuration
        db_config = {
            'host': CONFIG['Database']['host'],
            'port': CONFIG['Database']['port'],
            'username': CONFIG['Database']['username'],
            'password': CONFIG['Database']['password'],
            'database': CONFIG['Database']['database']
        }


        password_hash = generate_password_hash(admin_password)
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password_hash, emailID, role) VALUES (%s, %s, %s)', ('admin', password_hash, admin_email, 'admin'))
        conn.commit()
        #conn.close()
    
        # Read the existing Python configuration file
        with open('config/config.py', 'r') as py_file:
            python_code = py_file.read()
    
        # Extract CONFIG dictionary from the Python code
        exec(python_code, globals())
        config_data = globals().get('CONFIG', {})

        # Update the nested configuration
        config_data['Admin']['emailID'] = admin_email
        config_data['Datastore']['BackupPath'] = backup_path 
        config_data['Encrypt']['flask_enc_key'] = fernet_key
        config_data['FlaskSession']['key'] = flask_secret_key
        config_data['FlaskSession']['prefix'] = flask_session_prefix
    
        # Convert the updated dictionary to JSON format
        json_config = json.dumps(config_data, indent=4)
    
        # Write the updated JSON data back to the Python configuration file
        with open('config/config.py', 'w') as py_file:
            py_file.write(f'CONFIG = {json_config}')

        flash("Components setup completed", 'success')

        # If all checks pass, proceed to Page 3
        return redirect('/setup3')
    
    encrypt_key = get_or_generate_key()
    return render_template('setup2.html', key=encrypt_key)

#@app.route('/smtp_config')
def setup3():
    if request.method == 'POST':
        smtp_server = request.form['smtp_server']
        smtp_port = int(request.form['smtp_port'])
        username = request.form['username']
        password = request.form['password']
    
        # Encrypt the password before storing it
        encrypted_password = encrypt_password(password)
    
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Update SMTP data in the database
        query = """
            INSERT INTO smtp_config (id, smtp_server, smtp_port, username, encrypted_password)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            smtp_server = VALUES(smtp_server),
            smtp_port = VALUES(smtp_port),
            username = VALUES(username),
            encrypted_password = VALUES(encrypted_password)
        """
        data = (1, smtp_server, smtp_port, username, encrypted_password)
        cursor.execute(query, data)
    
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        # Read the existing Python configuration file
        with open('config/config.py', 'r') as py_file:
            python_code = py_file.read()

        # Extract CONFIG dictionary from the Python code
        exec(python_code, globals())
        config_data = globals().get('CONFIG', {})

        # Update the nested configuration
        config_data['SMTP']['server'] = smtp_server
        config_data['SMTP']['port'] = smtp_port
        config_data['SMTP']['username'] = username

        # Convert the updated dictionary to JSON format
        json_config = json.dumps(config_data, indent=4)

        # Write the updated JSON data back to the Python configuration file
        with open('config/config.py', 'w') as py_file:
            py_file.write(f'CONFIG = {json_config}')

        flash("SMTP Configuration Saved!!", 'success')
        return redirect('/setup4')
    
    return render_template('smtp_step1_config.html')

# Database connection configuration
db_config = {
    'host': CONFIG['Database']['host'],
    'port': CONFIG['Database']['port'],
    'username': CONFIG['Database']['username'],
    'password': CONFIG['Database']['password'],
    'database': CONFIG['Database']['database']
}
#@app.route('/smtp_config')
def setup4():
    if request.method == 'POST':
        # Check the action value from the form
        action = request.form.get('action')

        if action == 'test_email':
            # Retrieve SMTP configuration from the database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT smtp_server, smtp_port, username, encrypted_password FROM smtp_config WHERE id = 1")
            smtp_config = cursor.fetchone()
            conn.close()
        
            if smtp_config:
                smtp_server, smtp_port, username, encrypted_password = smtp_config
                password = decrypt_password(encrypted_password)
        
                # Retrieve email details from the form
                sender_name = "AirBackupX Alert"
                receiver_email = request.form['receiver_email']
                subject = request.form['subject']
                message_body = request.form['message_body']
        
                # Create Email Message
                msg = EmailMessage()
                msg.set_content(message_body)
                msg["Subject"] = subject
                msg["From"] = f"{sender_name} <{username}>"
                msg["To"] = receiver_email
        
                # Establish a Secure Session with SMTP Server
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()  # Upgrade the connection to a secure, encrypted SSL connection
                server.login(username, password)
        
                # Send Email
                try:
                    server.send_message(msg)
                    #return "Email sent successfully!"
                    flash("Email sent successfully!", 'success')
                    return redirect('/setup4')
                except Exception as e:
                    flash("SMTP Failure", 'error')
                    return redirect('/setup4')
                    #return f"Error: Unable to send email. {e}"
                finally:
                    # Close the SMTP server connection
                    server.quit()
            else:
                #return "SMTP configuration not found in the database."
                flash("SMTP configuration not found in the database.", 'error')
                return redirect(url_for('/setup3'))
        elif action == 'complete_setup':
            # Create a setup.lock file in the filesystem
            with open('setup.lock', 'w') as lock_file:
                lock_file.write('Setup completed')

            # Redirect to the login route after setup completion
            return redirect('/')

    # Connect to the database and retrieve existing SMTP configuration (except password)
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, smtp_server, smtp_port, username FROM smtp_config WHERE id = 1")
    smtp_config = cursor.fetchone()
    conn.close()
    return render_template('smtp_step2_config.html', smtp_config=smtp_config)
