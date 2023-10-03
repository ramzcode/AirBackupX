import mysql.connector
from datetime import datetime

# Establish a connection to the MySQL database
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='hack',
    database='passwords_db'
)

# Create a cursor object to interact with the database
cursor = connection.cursor()

# Sample backup information
backup_info = {
    'device_name': 'CiscoRouter2',
    'site_name': 'SiteBB',
    'type': 'Router',
    'username': 'admin',
    'exit_status': 'Failed',
    'file_name': 'backup_file_20231002.txt'
}

# Insert backup record into the database
insert_query = """
    INSERT INTO backup_records (backup_date, device_name, site_name, type, username, exit_status, file_name)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

values = (datetime.now(), backup_info['device_name'], backup_info['site_name'], backup_info['type'],
          backup_info['username'], backup_info['exit_status'], backup_info['file_name'])

cursor.execute(insert_query, values)

# Commit the changes and close the connection
connection.commit()
cursor.close()
connection.close()

