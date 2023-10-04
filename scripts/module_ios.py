from netmiko import ConnectHandler
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

def process_device(device_name, username, decrypted_password, group_name, device_type):
    # Initialize net_connect to None
    net_connect = None

    # DB backup information content
    backup_info = {
        'device_name': device_name,
        'site_name': group_name,
        'type': device_type,
        'username': username,
    }

    try:
        # Cisco IOS device details
        ios_device = {
            'device_type': 'cisco_ios',
            'ip': device_name,
            'username': username,
            'password': decrypted_password,
            'secret': 'admin',
        }

        net_connect = ConnectHandler(**ios_device)
        print(f"Connected to {device_name}")

        net_connect.enable()
        output = net_connect.send_command('show running-config')

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        config_file_path = f"/Users/ram/Downloads/AirBackupX/Backups/config_backup_{device_name}_{timestamp}.txt"
        with open(config_file_path, 'w') as config_file:
            config_file.write(output)

        print(f"Configuration saved to {config_file_path}")

        #exit_status = 'Success'

        # Insert backup record into the database
        insert_query = """
            INSERT INTO backup_records (backup_date, device_name, site_name, type, username, exit_status, file_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (datetime.now(), backup_info['device_name'], backup_info['site_name'], backup_info['type'], backup_info['username'], 'Success', config_file_path)

        cursor.execute(insert_query, values)

        # Commit the changes
        connection.commit()

    except Exception as e:
        print(f"Failed to backup configuration for {device_name}: {str(e)}")
        #exit_status = 'Failed'
        insert_query = """
            INSERT INTO backup_records (backup_date, device_name, site_name, type, username, exit_status, file_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (datetime.now(), backup_info['device_name'], backup_info['site_name'], backup_info['type'], backup_info['username'], 'Failed', 'NA')

        cursor.execute(insert_query, values)

        # Commit the changes
        connection.commit()

    finally:
        # Disconnect only if net_connect is assigned
        if net_connect:
            net_connect.disconnect()

# Example usage
# process_device(device_name, username, decrypted_password, group_name, device_type)
