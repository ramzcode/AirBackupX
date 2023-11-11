from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import request, redirect, flash, url_for
from app import app
import os
import csv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet, InvalidToken
from config.config  import CONFIG

db_url = f"mysql+mysqlconnector://{CONFIG['Database']['username']}:{CONFIG['Database']['password']}@{CONFIG['Database']['host']}/{CONFIG['Database']['database']}"

# Create engine and session
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class DeviceRecord(Base):
    __tablename__ = 'passwords'
    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    device = Column(String(255), unique=True)
    encrypted_password = Column(String(255))
    group_name = Column(String(255))
    type = Column(String(255))

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload(methods=['POST']):
    if 'csv_file' not in request.files:
        # No file part
        return redirect(request.url)
    file = request.files['csv_file']
    if file.filename == '':
        # No selected file
        return redirect(request.url)
    if file and allowed_file(file.filename):
        # Secure the filename and save it to the uploads folder
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Process the uploaded CSV file
        process_csv(file_path)
        flash("File uploaded and processed successfully.", 'success')
        return redirect(url_for('dashboard'))
    else:
        # Invalid file type
        return "Invalid file type. Please upload a CSV file."

def process_csv(file_path):
    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        session = Session()
        for row in csv_reader:
            username = row['username']
            device = row['device']
            password = row['encrypted_password']
            encrypted_password = encrypt_password(password)
            group_name = row['group_name']
            type = row['type']
            new_record = DeviceRecord(username=username, device=device, encrypted_password=encrypted_password, group_name=group_name, type=type)
            session.add(new_record)
        session.commit()
        session.close()
    os.remove(file_path)  # Remove the uploaded CSV file after processing

