from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, abort, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_session import Session
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from cryptography.fernet import Fernet, InvalidToken
import mysql.connector
from functools import wraps
import os
import json
from crontab import CronTab
import uuid
import subprocess
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash  # Import password hashing function
import logging
import logging.handlers
import pyotp
#from routes.widgets import widgets_bp
#from routes.widgets import widget_type, widget_device, widget_jobs, widget_site
from routes.widgets import fetch_widgets_data
from routes.dev_import import upload
from routes.smtp_config import smtp_config_ui, update_smtp, send_email
from routes.abx_setup import setup1, setup2, setup3, setup4
from routes.emailer import send_registration_email
from config.config  import CONFIG

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False  # Session will expire when the browser is closed
app.config['SESSION_USE_SIGNER'] = True  # Session data is signed for security
app.config['SESSION_KEY_PREFIX'] = CONFIG['FlaskSession']['prefix']  # Replace with your own prefix
app.secret_key = CONFIG['FlaskSession']['key'] # Change this to a strong, random value
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{CONFIG['Database']['username']}:{CONFIG['Database']['password']}@{CONFIG['Database']['host']}/{CONFIG['Database']['database']}"   # Replace with your database URL
db = SQLAlchemy(app)
cache = Cache(app)

# Register the widgets blueprint
#app.register_blueprint(widgets_bp, url_prefix='/widgets_type')

# Import routes after creating the Flask app and SQLAlchemy instance
#from routes import widgets
# Register the route function with Flask

class BackupRecord(db.Model):
    __tablename__ = 'backup_records'  # Specify the table name if different from the class name
    id = db.Column(db.Integer, primary_key=True)
    backup_date = db.Column(db.DateTime)
    device_name = db.Column(db.String(255))
    site_name = db.Column(db.String(255))
    type = db.Column(db.String(255))  # Adjust the data type and length as per your schema
    username = db.Column(db.String(255))  # Adjust the data type and length as per your schema
    exit_status = db.Column(db.String(50))  # Adjust the data type and length as per your schema
    file_name = db.Column(db.String(255))  # Adjust the data type and length as per your schema

class DeviceRecord(db.Model):
    __tablename__ = 'passwords'
    username = db.Column(db.String(255))
    device = db.Column(db.String(255), primary_key=True, unique=True)
    encrypted_password = db.Column(db.String(255))
    group_name = db.Column(db.String(255))
    type = db.Column(db.String(255))

Session(app)
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Flask-Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Function to check database connection
def check_db_connection():
    if os.path.exists('setup.lock'):
        with app.app_context():
            try:
                # Attempt to connect to the database
                result = db.session.execute(text('SELECT 1'))
                return True
            except:
                return False

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Middleware to store the client IP in the thread-local storage
@app.before_request
def store_client_ip():
    request.client_ip = request.remote_addr

# Register routes using add_url_rule()
#app.add_url_rule('/widgets_device', 'widget_device', widget_device)
app.add_url_rule('/smtp_config_ui', 'smtp_config_ui', smtp_config_ui)
app.add_url_rule('/update_smtp', 'update_smtp', update_smtp, methods=['POST'])
app.add_url_rule('/send_email', 'send_email', send_email, methods=['POST'])
app.add_url_rule('/fetch_widgets_data', 'fetch_widgets_data', fetch_widgets_data)
app.add_url_rule('/upload', 'upload', upload, methods=['POST'])
app.add_url_rule('/setup1', 'setup1', setup1, methods=['POST', 'GET'])
app.add_url_rule('/setup2', 'setup2', setup2, methods=['POST', 'GET'])
app.add_url_rule('/setup3', 'setup3', setup3, methods=['POST', 'GET'])
app.add_url_rule('/setup4', 'setup4', setup4, methods=['POST', 'GET'])

# Configure logging
custom_log_file = 'AirBackupX_messages.log'  # Specify the log file path

# Create a custom log formatter
custom_logger = logging.getLogger('custom_logger')
custom_logger.setLevel(logging.INFO)  # Set the desired logging level for custom logs (e.g., INFO)

# Define the log format for your custom logs (includes IP info)
custom_log_format = '[%(asctime)s] [%(ip)s] [%(levelname)s]: %(message)s'
# Configure a custom log handler for your custom logger
custom_log_handler = logging.handlers.TimedRotatingFileHandler(
    custom_log_file,
    when="midnight",
    interval=1,
    backupCount=7
)
custom_log_handler.setFormatter(logging.Formatter(custom_log_format))

# Set the custom log handler's filter to include IP information
class IPLogFilter(logging.Filter):
    def filter(self, record):
        record.ip = request.client_ip
        return True

custom_log_handler.addFilter(IPLogFilter())

# Add the custom log handler to the custom logger
custom_logger.addHandler(custom_log_handler)

# Define the User class for Flask-Login

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# @app.before_request
# def check_session_timeout():
#     # Get the current session's last access time
#     last_access_time = session.get('last_access_time')

#     if last_access_time is not None:
#         # Calculate the elapsed time since the last access
#         elapsed_time = datetime.now() - last_access_time

#         # Set your desired session timeout duration (e.g., 30 minutes)
#         session_timeout_duration = timedelta(minutes=5)

#         if elapsed_time > session_timeout_duration:
#             # Session has expired, clear the session and redirect to the login page
#             session.clear()
#             flash('Your session has expired due to inactivity.', 'info')
#             return redirect(url_for('login'))
#     # Update the last access time for the session
#     session['last_access_time'] = datetime.now()

@app.before_request
def check_session_timeout():
    # Exclude certain routes from session timeout check
    excluded_routes = ['login', 'logout']  # Add more routes if needed

    if request.endpoint and request.endpoint not in excluded_routes:
        last_access_time = session.get('last_access_time')

        if last_access_time is not None:
            elapsed_time = datetime.now() - last_access_time
            session_timeout_duration = timedelta(minutes=5)

            if elapsed_time > session_timeout_duration:
                session.clear()
                flash('Your session has expired due to inactivity.', 'info')
                return redirect(url_for('login'))

    # Update the last access time for the session
    session['last_access_time'] = datetime.now()


@login_manager.user_loader
def load_user(username):
    # Load a user from the database based on the provided user_id
    # Replace this code with your actual database query logic
    cursor.execute('SELECT id, username, password_hash FROM users WHERE id = %s', (username,))
    result = cursor.fetchone()
    
    if result:
        user_id, username, password_hash = result
        # Create a User object with the fetched data
        user = User(user_id, username, password_hash)
        return user
    
    # Return None if user_id is not found in the database
    return None

def requires_admin(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        user_id = current_user.username
        # Check if the user's role is in the cache
        role = cache.get(f'user_role:{user_id}')
        if role is None:
            # If not in cache, query the database and store the result in the cache
            # Connect to MySQL/MariaDB database
            db_config = {
                'host': CONFIG['Database']['host'],
                'port': CONFIG['Database']['port'],
                'user': CONFIG['Database']['username'],
                'password': CONFIG['Database']['password'],
                'database': CONFIG['Database']['database']
            }
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute('SELECT role FROM users WHERE username = %s', (user_id,))
            role = cursor.fetchone()
            #role = get_user_role(user_id)  # Replace with your database query function
            cache.set(f'user_role:{user_id}', role, timeout=3600)  # Cache for 1 hour (adjust timeout as needed)
            # Close the cursor and connection after the operations are done
            cursor.close()
            conn.close()

        if role and role[0] == 'admin':
            return view_func(*args, **kwargs)
        else:
            # Redirect to a different route or show an access denied message
            flash('Unauthorized Access', 'error')
            return redirect(url_for('dashboard'))
    return wrapped

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user, email=CONFIG['Admin']['emailID'])


@app.route('/user_registration', methods=['GET', 'POST'])
@login_required
@requires_admin
def user_registration():
    # # Check if the current user's username is "2222"
    # if current_user.username == "2222":
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        emailID = request.form['emailID']
        role = request.form['role']
        confirm_password = request.form['confirm_password']

        # Check if the username and password are provided
        if not username or not password or not confirm_password:
            flash('Both username and password are required.', 'error')
            return redirect(url_for('user_registration.html'))

        # Check if the passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please enter the same password twice.', 'error')
            return render_template('user_registration.html')

        # Check if the username already exists in the database
        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
        else:
            # Generate a random OTP secret
            totp_secret = pyotp.random_base32()
            # Hash and store the user's password
            password_hash = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password_hash, emailID, role, totp_secret) VALUES (%s, %s, %s, %s, %s)', (username, password_hash, emailID, role, totp_secret))
            conn.commit()

            send_registration_email(username=username, email=emailID, totp_secret=totp_secret)

            flash('Registration successful! Account Created', 'success')
            # If 'next' is provided in the query string, redirect there, otherwise go to 'dashboard'
            #next_page = request.args.get('next', None)
            return redirect(url_for('dashboard'))
            #return redirect(url_for('login'))

    return render_template('user_registration.html')
    # else:
    #     flash('Unauthorized Access', 'error')
    #     return redirect(url_for('dashboard'))

@app.route('/reset_password', methods=['POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check if the new password  and new confirm password are provided
        if not new_password or not confirm_password:
            flash('Both new password and confirm password are required.', 'error')
            return redirect(url_for('profile'))

        # Check if the new password and confirm password match
        if new_password == confirm_password:
            # Update the user's password in the database
            new_password_hash = generate_password_hash(new_password)
            cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (new_password_hash, current_user.id))
            conn.commit()

            flash('Password Reset successful! You can now log in with new password.', 'success')
            return redirect(url_for('logout'))
        else:
            flash('Password Reset failed', 'error')

    return redirect(url_for('profile'))


@app.route('/', methods=['GET', 'POST'])
def login():
    if os.path.exists('setup.lock'):
        # Handle login logic
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            otp = request.form['otp']

            # Check if the username and password are provided
            if not username or not password or not otp:
                flash('Both username, password and OTP are required.', 'error')
                return redirect(url_for('login'))
    
            # Query the database to retrieve the user's hashed password
            cursor.execute('SELECT id, username, password_hash, totp_secret FROM users WHERE username = %s', (username,))
            result = cursor.fetchone()
    
            if result:
                totp = pyotp.TOTP(result[3])
                if totp.verify(otp):
                    if check_password_hash(result[2], password):
                        # If the username and password are valid, log in the user
                        user = User(result[0], result[1], result[2])
                        login_user(user)
        
                        # Initialize the session and set the last access time
                        session['last_access_time'] = datetime.now()
        
                        flash('Login successful!', 'success')
                        custom_logger.info(f'User {username} logged in Successfully')
                        # Redirect the user to the stored 'next' URL or '/dashboard' if it doesn't exist
                        #next_url = request.args.get('next', url_for('dashboard'))
                        #return redirect(next_url)
                        #next_page = request.args.get('next')
                        #return render_template('login.html', next_page=next_page)
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Login failed. Please check your credentials.', 'error')
                        return render_template('login.html')
                else:
                    flash('Invalid OTP. Please enter a valid OTP.', 'error')
                    return render_template('login.html')
            else:
                flash('Account Does Not Exist. Please check your credentials.', 'error')
                return render_template('login.html')
        else:
            return render_template('login.html')
    else:
        return render_template('setup1.html')

#@app.route('/', methods=['GET', 'POST'])
#def login():
#    if request.method == 'POST':
#        username = request.form['username']\
#        password = request.form['password']
#
#        # Check if the username and password are provided
#        if not username or not password:
#            flash('Both username and password are required.', 'error')
#            return redirect(url_for('login'))
#
#        # Query the database to retrieve the user's hashed password
#        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = %s', (username,))
#        result = cursor.fetchone()
#
#        if result and check_password_hash(result[2], password):
#            # If the username and password are valid, log in the user
#            user = User(result[0], result[1], result[2])
#            login_user(user)
#
#            # Initialize the session and set the last access time
#            session['last_access_time'] = datetime.now()
#
#            flash('Login successful!', 'success')
#            custom_logger.info(f'User {username} logged in Successfully')
#            # Redirect the user to the stored 'next' URL or '/dashboard' if it doesn't exist
#            #next_url = request.args.get('next', url_for('dashboard'))
#            #return redirect(next_url)
#            #next_page = request.args.get('next')
#            #return render_template('login.html', next_page=next_page)
#            return redirect(url_for('dashboard'))
#
#        flash('Login failed. Please check your credentials.', 'error')
#
#        # Capture the 'next' query parameter if it exists
#        #next_page = request.args.get('next')
#
#        #if next_page:
#            # Store 'next' in the session for later use
#           # session['next'] = next_page
#
#    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
    #return redirect(url_for('login', flash_message='You have been logged out.'))

# Define your local backup directory here
local_directory = CONFIG['Datastore']['BackupPath']  # Replace with the path to your local directory

@app.route('/explorer')
def explorer():
    contents = list_directory_contents(local_directory)
    return render_template('explorer.html', folder_path=local_directory, contents=contents)


@app.route('/download/<path:file_path>')
def download_file(file_path):
    full_file_path = os.path.join(local_directory, file_path)

    # Check if the file exists
    if os.path.exists(full_file_path):
        try:
            # Use send_from_directory to serve the file as an attachment
            return send_from_directory(local_directory, file_path, as_attachment=True)
        except Exception as e:
            return f"Error downloading file: {str(e)}"
    else:
        abort(404)

@app.route('/explore/<path:folder_path>')
def explore_directory(folder_path):
    full_folder_path = os.path.join(local_directory, folder_path)
    contents = list_directory_contents(full_folder_path)
    return render_template('explorer.html', folder_path=folder_path, contents=contents)

@app.route('/get_contents/<path:folder_path>')
def get_contents(folder_path):
    full_folder_path = os.path.join(local_directory, folder_path)
    contents = list_directory_contents(full_folder_path)
    return jsonify(contents)

def list_directory_contents(directory_path):
    try:
        contents = []
        for item in os.listdir(directory_path):
            full_item_path = os.path.join(directory_path, item)
            is_directory = os.path.isdir(full_item_path)
            timestamp = get_timestamp(full_item_path)
            relative_path = os.path.relpath(full_item_path, local_directory)
            contents.append((relative_path, is_directory, timestamp))
        return contents
    except Exception as e:
        return [str(e)]

def get_timestamp(file_path):
    try:
        timestamp = os.path.getmtime(file_path)
        return timestamp
    except Exception as e:
        return None

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
    'host': CONFIG['Database']['host'],
    'port': CONFIG['Database']['port'],
    'user': CONFIG['Database']['username'],
    'password': CONFIG['Database']['password'],
    'database': CONFIG['Database']['database']
}

if check_db_connection():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

# # Create the 'passwords' table if it doesn't exist
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS passwords (
#         username VARCHAR(255),
#         device VARCHAR(255) UNIQUE,
#         encrypted_password BLOB
#     )
# ''')

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS smtp_config (
#         id INT PRIMARY KEY AUTO_INCREMENT,
#         smtp_server VARCHAR(255),
#         smtp_port INT,
#         username VARCHAR(255) UNIQUE,
#         encrypted_password BLOB
# );
# ''')

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS groups (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         name VARCHAR(255) UNIQUE
#     )
# ''')

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS types (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         name VARCHAR(255) UNIQUE
#     )
# ''')


# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS users (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         username VARCHAR(255) UNIQUE NOT NULL,
#         password_hash VARCHAR(255) NOT NULL
#     )
# ''')

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS cron_jobs (
#         job_id VARCHAR(255) PRIMARY KEY,
#         site_name VARCHAR(255),
#         script_path VARCHAR(255),
#         minute VARCHAR(10),
#         hour VARCHAR(10),
#         day VARCHAR(10),
#         month VARCHAR(10),
#         day_of_week VARCHAR(10)
#     )
# ''')

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS backup_records (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         backup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         device_name VARCHAR(255) NOT NULL,
#         site_name VARCHAR(255) NOT NULL,
#         type VARCHAR(255) NOT NULL,
#         username VARCHAR(255) NOT NULL,
#         exit_status ENUM('failed', 'succeeded') NOT NULL,
#         file_name VARCHAR(255) NOT NULL
#     )
# ''')


# #cursor.execute('''
# #    ALTER TABLE passwords
# #    ADD COLUMN type VARCHAR(255)
# #''')

# conn.commit()

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
#    cursor = None
#    try:
#        conn = mysql.connector.connect(**db_config)
#        cursor = conn.cursor()
#        cursor.execute('SELECT device FROM passwords')
#        results = cursor.fetchall()
#        devices = [result[0] for result in results]
#        return devices
#    except Exception as e:
#        # Handle exceptions, log errors, etc.
#        return "error"
#    finally:
#        if cursor:
#            cursor.close()
#        if conn and conn.is_connected():
#            conn.close()
#def list_devices():
    devices = DeviceRecord.query.all()
    return [device.device for device in devices]

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

#@app.route('/')
#def login():
#    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    devices = list_devices()
    groups = list_groups()
    types = list_types()
    return render_template('dashboard.html', devices=devices, groups=groups, types=types)

@app.route('/devicemgmt')
@login_required
def devicemgmt():
    devices = list_devices()
    groups = list_groups()
    types = list_types()
    return render_template('devicemgmt.html', devices=devices, groups=groups, types=types)

@app.route('/sitemgmt')
@login_required
def sitemgmt():
    devices = list_devices()
    groups = list_groups()
    types = list_types()
    return render_template('sitemgmt.html', devices=devices, groups=groups, types=types)

@app.route('/typemgmt')
@login_required
def typemgmt():
    devices = list_devices()
    groups = list_groups()
    types = list_types()
    return render_template('typemgmt.html', devices=devices, groups=groups, types=types)

@app.route('/credretrieve')
@login_required
def credretrieve():
    return render_template('credretrieve.html')

@app.route('/create', methods=['POST'])
@login_required
@requires_admin
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

    return redirect(url_for('dashboard'))

@app.route('/retrieve', methods=['POST', 'GET'])
@login_required
@requires_admin
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
@requires_admin
@login_required
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
        return redirect(url_for('dashboard'))

    return render_template('edit.html', device=device, old_username=old_username)


# Function to delete credentials by device name
@app.route('/delete/<device>', methods=['GET'])
@requires_admin
@login_required
def delete(device):
    try:
        cursor.execute('DELETE FROM passwords WHERE device = %s', (device,))
        conn.commit()
        flash(f"Device '{device}' deleted successfully!", 'success')
    except Exception as e:
        flash(f"An error occurred: {e}", 'error')

    return redirect(url_for('dashboard'))

@app.route('/create_group', methods=['POST'])
@login_required
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

    return redirect(url_for('dashboard'))

@app.route('/delete_group', methods=['GET', 'POST'])
@requires_admin
@login_required
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

    return redirect(url_for('dashboard'))

@app.route('/update_device_group/<device>', methods=['POST'])
@login_required
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
    return redirect(url_for('dashboard'))


@app.route('/create_type', methods=['POST'])
@login_required
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

    return redirect(url_for('dashboard'))

@app.route('/delete_type', methods=['GET', 'POST'])
@requires_admin
@login_required
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

    return redirect(url_for('dashboard'))

# Function to create a valid cron schedule string
def create_cron_schedule(minute, hour, day, month, day_of_week):
    cron_string = f"{minute} {hour} {day} {month} {day_of_week}"
    return cron_string

@app.route('/schedule_cron_job', methods=['GET', 'POST'])
@login_required
def schedule_cron_job():
    if request.method == 'POST':
        site_name = request.form.get('site_name')
        script_file = f"/Users/ram/Downloads/AirBackupX/scripts/{site_name}.py"

        # Ensure that the parent directory exists, create it if it doesn't
        parent_directory = os.path.dirname(script_file)
        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)
        
        # Check if the script file exists, and create it with content if it doesn't
        if not os.path.exists(script_file):
            # Create the script file and add your desired content
            with open(script_file, 'w') as file:
                file.write("BackupCodeContentGoesHereblablaablaaaa\n")
        
        minute = request.form.get('minute')
        hour = request.form.get('hour')
        day = request.form.get('day')
        month = request.form.get('month')
        day_of_week = request.form.get('day_of_week')

        # Create a valid cron schedule string
        cron_schedule = create_cron_schedule(minute, hour, day, month, day_of_week)

        # Generate a unique job ID (e.g., using UUID)
        job_id = str(uuid.uuid4())

        # Initialize a CronTab object
        cron = CronTab(user='ram')  # Replace 'your_username' with the appropriate username

        # Create a new cron job and set its command
        job = cron.new(command=f'python {script_file}')

        # Set the cron schedule using the cron_schedule string
        job.setall(cron_schedule)

        # Write the cron job to the user's crontab
        cron.write()

        # Store the cron job and associated data in the cron_jobs dictionary
        cursor.execute('''
            INSERT INTO cron_jobs (job_id, site_name, script_path, minute, hour, day, month, day_of_week)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (job_id, site_name, script_file, minute, hour, day, month, day_of_week))
        conn.commit()

        flash('Cron job scheduled successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('schedule_cron_job.html')

@app.route('/list_cron_jobs', methods=['GET'])
@login_required
def list_cron_jobs():
    cursor.execute('SELECT * FROM cron_jobs')
    cron_job_data = cursor.fetchall()
    return render_template('list_cron_jobs.html', cron_job_data=cron_job_data)


@app.route('/edit_cron_job/<job_id>', methods=['GET', 'POST'])
@login_required
def edit_cron_job(job_id):
    if request.method == 'POST':
        cursor.execute('SELECT script_path FROM cron_jobs WHERE job_id = %s', (job_id,))
        result = cursor.fetchone()

        if result:
            script_path = result[0]

            # Remove the cron job from the user's crontab
            cron = CronTab(user='ram')  # Replace 'your_username' with the appropriate username
            jobs = cron.find_command(script_path)

            for job in jobs:
                cron.remove(job)
            cron.write()

            #Fetch Form data to update
            minute = request.form.get('minute')
            hour = request.form.get('hour')
            day = request.form.get('day')
            month = request.form.get('month')
            day_of_week = request.form.get('day_of_week')

            # Create a valid cron schedule string
            cron_schedule = create_cron_schedule(minute, hour, day, month, day_of_week)
            # Create a new cron job and set its command
            job = cron.new(command=f'python {script_path}')
            # Set the cron schedule using the cron_schedule string
            job.setall(cron_schedule)

            # Write the cron job to the user's crontab
            cron.write()

            #Update the cron job details in the database
            cursor.execute('''
                UPDATE cron_jobs
                SET minute = %s, hour = %s, day = %s, month = %s, day_of_week = %s
                WHERE job_id = %s
                ''', (minute, hour, day, month, day_of_week, job_id))
            conn.commit()

            flash('Cron job updated successfully!', 'success')
            return redirect(url_for('list_cron_jobs'))
        else:
            flash('Cron job not found.', 'error')
            return redirect(url_for('list_cron_jobs'))

    return render_template('edit_cron_job.html')


@app.route('/delete_cron_job/<job_id>', methods=['GET', 'POST'])
@requires_admin
@login_required
def delete_cron_job(job_id):
    if request.method == 'POST':
        # Retrieve the job details from the database based on job_id
        cursor.execute('SELECT script_path FROM cron_jobs WHERE job_id = %s', (job_id,))
        result = cursor.fetchone()

        if result:
            script_path = result[0]

            # Remove the cron job from the user's crontab
            cron = CronTab(user='ram')  # Replace 'your_username' with the appropriate username
            jobs = cron.find_command(script_path)

            for job in jobs:
                cron.remove(job)
            cron.write()

            # Delete the entry from the cron_jobs table
            cursor.execute('DELETE FROM cron_jobs WHERE job_id = %s', (job_id,))
            conn.commit()

            flash('Cron job deleted successfully!', 'success')
            return redirect(url_for('list_cron_jobs'))
        else:
            flash('Cron job not found.', 'error')
            return redirect(url_for('list_cron_jobs'))

    return render_template('delete_cron_job.html')

@app.route('/runonce_cron_job/<job_id>', methods=['GET', 'POST'])
@login_required
def runonce_cron_job(job_id):
    if request.method == 'GET':
        # Retrieve the job details from the database based on job_id
        cursor.execute('SELECT script_path FROM cron_jobs WHERE job_id = %s', (job_id,))
        result = cursor.fetchone()

        if result:
            script_path = result[0]
            if os.path.exists(script_path):
                flash('Job Started Successfully', 'success')
                # Use subprocess to run the local command
                try:
                    subprocess.Popen(['python3.9', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except Exception as e:	
                    flash(f'Error running the script: {e}', 'error')
                return redirect(url_for('list_cron_jobs'))
            else:
                print('Script Not Found')
                raise FileNotFoundError('Script handling error, Please check with application owner')
        else:
            flash('Cron job not found.', 'error')
            return redirect(url_for('list_cron_jobs'))

    return redirect(url_for('list_cron_jobs'))

@app.route('/get_job_status/<site_name>', methods=['GET'])
def get_job_status(site_name):
    #log_file_path = f'{site_name}_runner.log'  # Update with the actual path to your log file
    log_file_path = 'runner.log'  # Update with the actual path to your log file
    default_status = 'Unknown'  # Default status if site name is not found in the log file

    site_statuses = {}  # Dictionary to store the latest status for each site

    # Read the log file and extract status based on site name
    try:
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                site, status = line.strip().split(':')
                # Update status for the site in the dictionary
                site_statuses[site] = status

        # Get the latest status for the requested site_name
        latest_status = site_statuses.get(site_name, default_status)
        return latest_status

    except FileNotFoundError:
        # Handle file not found error
        return default_status
    except Exception as e:
        # Handle other exceptions if necessary
        print(str(e))

    # Return default status if site name is not found in the log file
    return default_status


def get_all_users():
    try:
        cursor.execute('SELECT username FROM users')
        users = [result[0] for result in cursor.fetchall()]
        return users
    except Exception as e:
        print(f"Error fetching users from the database: {str(e)}")
        return []

# Function to delete a user by username
def delete_user_by_username(username):
    try:
        cursor.execute('DELETE FROM users WHERE username = %s', (username,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred while deleting user '{username}': {str(e)}", 'error')

@app.route('/delete_account', methods=['POST'])
@requires_admin
@login_required
def delete_account():
    if request.method == 'POST':
        # Get the list of users to delete from the form
        users_to_delete = request.form.getlist('delete_users[]')

        if not users_to_delete:
            flash('No users selected for deletion.', 'warning')
        else:
            # Loop through the selected users and delete their accounts
            for user in users_to_delete:
                cursor.execute('DELETE FROM users WHERE username = %s', (user,))
                conn.commit()
                flash(f'Account for user "{user}" deleted successfully.', 'success')

    return redirect(url_for('user_management'))


# Function to update a user's password by username
def update_user_password(username, new_password):
    try:
        password_hash = generate_password_hash(new_password)
        cursor.execute('UPDATE users SET password_hash = %s WHERE username = %s', (password_hash, username))
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred while resetting the password for user '{username}': {str(e)}", 'error')


#@app.route('/user_registration', methods=['GET', 'POST'])
#@login_required
#def user_registration():
#    if current_user.username == "2222":
#        return render_template('user_registration.html')
#    else:
#        flash('Unauthorized Access', 'error')
#        return redirect(url_for('dashboard'))

@app.route('/user_management', methods=['GET', 'POST'])
@requires_admin
@login_required
def user_management():
    if current_user.username == "2222":
        # List Users
        if request.method == 'GET':
            users = get_all_users()  # Implement this function to fetch all users
            return render_template('user_management.html', users=users)
    
        # Delete User
        if request.method == 'POST' and 'delete_username' in request.form:
            delete_username = request.form['delete_username']
            if delete_username:
                delete_user_by_username(delete_username)  # Implement this function to delete a user
                flash(f"User '{delete_username}' deleted successfully!", 'success')
    
        # Reset Password
        # Reset Password
        if request.method == 'POST' and 'reset_username' in request.form and 'new_password' in request.form:
            reset_username = request.form['reset_username']
            new_password = request.form['new_password']
            if reset_username and new_password:
                # Check if the user exists in the database before resetting the password
                cursor.execute('SELECT id FROM users WHERE username = %s', (reset_username,))
                existing_user = cursor.fetchone()
                if existing_user:
                    # User exists, proceed with password reset
                    new_password_hash = generate_password_hash(new_password)
                    cursor.execute('UPDATE users SET password_hash = %s WHERE username = %s',
                                   (new_password_hash, reset_username))
                    conn.commit()
                    flash(f"Password for user '{reset_username}' reset successfully!", 'success')
                else:
                    flash(f"User '{reset_username}' does not exist. Password reset failed.", 'error')
            else:
                flash("Both username and new password are required.", 'error')
        
        return redirect(url_for('user_management'))
    else:
        flash('Unauthorized Access', 'error')
        return redirect(url_for('dashboard'))

def list_backup_records():
    data = BackupRecord.query.all()
    #Convert the data to a list of dictionaries
    backup_records_list = []
    for record in data:
        backup_records_list.append({
            "backup_date": record.backup_date,
            "device_name": record.device_name,
            "site_name": record.site_name,
            "type": record.type,
            "username": record.username,
            "exit_status": record.exit_status,
            "file_name": record.file_name
        })
    
    # Return the data as JSON
    return (backup_records_list)

##Perfect One
@app.route('/backup_records')
def backup_records():
    # Query the database table and pass the data to the template
    data = BackupRecord.query.all()
    return render_template('backup_records.html', backup_records=data)

# @app.route('/backup_records')
# def backup_records():
#     # Query the database table and get the data
#     data = BackupRecord.query.all()
    
#     # Convert the data to a list of dictionaries
#     backup_records_list = []
#     for record in data:
#         backup_records_list.append({
#             "backup_date": record.backup_date,
#             "device_name": record.device_name,
#             "site_name": record.site_name,
#             "type": record.type,
#             "username": record.username,
#             "exit_status": record.exit_status,
#             "file_name": record.file_name
#         })
    
#     # Return the data as JSON
#     return jsonify(backup_records_list)

# # Route to display backup records
# @app.route('/backup_records')
# def backup_records():
#     backup_records = list_backup_records()
#     return render_template('backup_records.html', backup_records=backup_records)

# # Route to fetch updated backup records (server-side)
@app.route('/fetch_backup_records')
def fetch_backup_records():
    backup_records = list_backup_records()
    return jsonify(backup_records)

@app.route('/upload_link')
@login_required
def upload_link():
    return render_template('upload.html')

@app.route('/config_ui')
@requires_admin
@login_required
def config_ui():
    section_selected = request.args.get('section', 'section1')  # Default to section1 if not provided
    selected_section_keys = CONFIG.get(section_selected, {}).keys()  # Get keys of the selected section or an empty list if not found
    return render_template('config.html', config=CONFIG, section_selected=section_selected, selected_section_keys=selected_section_keys)

@app.route('/config_update', methods=['POST'])
def config_update():
    section = request.form['section']
    key = request.form['key']
    new_value = request.form['new_value']

    # Read the existing Python configuration file
    with open('config/config.py', 'r') as py_file:
        python_code = py_file.read()

    # Extract CONFIG dictionary from the Python code
    exec(python_code, globals())
    config_data = globals().get('CONFIG', {})

    # Update the nested configuration
    config_data[section][key] = new_value

    # Convert the updated dictionary to JSON format
    json_config = json.dumps(config_data, indent=4)

    # Write the updated JSON data back to the Python configuration file
    with open('config/config.py', 'w') as py_file:
        py_file.write(f'CONFIG = {json_config}')

    return redirect('/config_ui')

#def allowed_file(filename):
#    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
#@app.route('/upload', methods=['POST'])
#def upload_file():
#    if 'csv_file' not in request.files:
#        # No file part
#        return redirect(request.url)
#    file = request.files['csv_file']
#    if file.filename == '':
#        # No selected file
#        return redirect(request.url)
#    if file and allowed_file(file.filename):
#        # Secure the filename and save it to the uploads folder
#        filename = secure_filename(file.filename)
#        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#        file.save(file_path)
#        # Process the uploaded CSV file
#        process_csv(file_path)
#        db.session.commit()
#        db.session.close()
#        flash("File uploaded and processed successfully.", 'success')
#        return redirect(url_for('dashboard')) 
#    else:
#        # Invalid file type
#        return "Invalid file type. Please upload a CSV file."
#
#def process_csv(file_path):
#    with open(file_path, 'r') as file:
#        csv_reader = csv.DictReader(file)
#        for row in csv_reader:
#            username = row['username']
#            device = row['device']
#            password = row['encrypted_password']
#            encrypted_password = encrypt_password(password)
#            group_name = row['group_name']
#            type = row['type']
#            new_record = DeviceRecord(username=username, device=device, encrypted_password=encrypted_password, group_name=group_name, type=type)
#            db.session.add(new_record)
#            #db.session.commit()
#            #db.session.close()
#    os.remove(file_path)  # Remove the uploaded CSV file after processing

# Check database connection before starting the Flask app
if check_db_connection():
    if __name__ == '__main__':
        #app.run(debug=True)
        app.run(host='0.0.0.0', port=3030)
        conn.close()
else:
    # Exit the application if the database connection fails
    print('CRITICAL: Database not accessible, Fix and retry.')
    exit(24)