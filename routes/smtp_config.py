import mysql.connector
from flask import request, redirect, flash, url_for, render_template
from app import app
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet, InvalidToken
import smtplib
from email.message import EmailMessage
from config.config  import CONFIG

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

# Function to encrypt a password
def encrypt_password(password):
    encrypted_password = cipher_suite.encrypt(password.encode())
    return encrypted_password

# Connect to MySQL/MariaDB database
db_config = {
    'host': CONFIG['Database']['host'],
    'port': CONFIG['Database']['port'],
    'user': CONFIG['Database']['username'],
    'password': CONFIG['Database']['password'],
    'database': CONFIG['Database']['database']
}

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


#@app.route('/smtp_config')
def smtp_config_ui():
    # Connect to the database and retrieve existing SMTP configuration (except password)
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, smtp_server, smtp_port, username FROM smtp_config WHERE id = 1")
    smtp_config = cursor.fetchone()
    conn.close()
    return render_template('smtp_config.html', smtp_config=smtp_config)

#@app.route('/update_smtp', methods=['POST'])
def update_smtp():
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
    query = "INSERT INTO smtp_config (smtp_server, smtp_port, username, encrypted_password) VALUES (%s, %s, %s, %s)"
    data = (smtp_server, smtp_port, username, encrypted_password)
    cursor.execute(query, data)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    flash("SMTP Configuration Saved!!", 'success')
    return redirect(url_for('dashboard'))

#@app.route('/send_email', methods=['POST'])
def send_email():
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
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash("SMTP Failure", 'success')
            return redirect(url_for('dashboard'))
            #return f"Error: Unable to send email. {e}"
        finally:
            # Close the SMTP server connection
            server.quit()
    else:
        #return "SMTP configuration not found in the database."
        flash("SMTP configuration not found in the database.", 'error')
        return redirect(url_for('dashboard'))
