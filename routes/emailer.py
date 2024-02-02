import mysql.connector
from flask import request, redirect, flash, url_for, render_template
from app import app
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet, InvalidToken
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import qrcode
from io import BytesIO
from config.config  import CONFIG
import pyotp

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
    'host': CONFIG['Database']['host'],
    'port': CONFIG['Database']['port'],
    'user': CONFIG['Database']['username'],
    'password': CONFIG['Database']['password'],
    'database': CONFIG['Database']['database']
}

# Function to decrypt a password
def decrypt_password(encrypted_password):
    try:
        decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
        return decrypted_password
    except InvalidToken:
        return "Invalid token (possibly corrupted or tampered data)"
    
def send_registration_email(username, email, totp_secret):
    # Retrieve SMTP configuration from the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT smtp_server, smtp_port, username, encrypted_password FROM smtp_config WHERE id = 1")
    smtp_config = cursor.fetchone()
    conn.close()

    reg_user = username
    reg_user_email = email

    if smtp_config:
        smtp_server, smtp_port, username, encrypted_password = smtp_config
        password = decrypt_password(encrypted_password)

        # Generate a TOTP URI for the user
        totp_uri = pyotp.TOTP(totp_secret).provisioning_uri(name=reg_user, issuer_name='AirBackupX')

        # Generate a QR code
        img = qrcode.make(totp_uri)

        # Save the QR code to a BytesIO object
        img_bytes = BytesIO()
        img.save(img_bytes)
        img_bytes.seek(0)


        # Retrieve email details from the form
        sender_name = "AirBackupX Registration"
        receiver_email = reg_user_email
        subject = 'Welcome to AirbackupX'
        message_body = f'Hello {reg_user},\n\nWelcome to AirbackupX!'

        # Create Email Message
        msg = MIMEMultipart()
        #msg = EmailMessage()
        # Attach the QR code image
        qr_code_attachment = MIMEImage(img_bytes.read(), name='AirBackupX-QR-Code.png')
        msg.attach(qr_code_attachment)
        text_part = MIMEText(message_body, 'plain')
        msg.attach(text_part)
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
            flash("Registration Email sent to user successfully!", 'success')
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