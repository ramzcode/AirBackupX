#from flask import Blueprint, jsonify
#from db_connection import db_session
#from models.db_models import TypeRecord
import mysql.connector
from flask import jsonify

# widgets_bp = Blueprint('widgets', __name__)

# @widgets_bp.route('/widgets_type', methods=['GET'])
# def widgets_type():
#     total_count = db_session.query(db.func.count(TypeRecord.id)).scalar()
#     total_types = {'total_count': total_count}
#     return jsonify(count=total_types)

#app.add_url_rule('/widget_type', 'widget_type', widget_type)

# Connect to MySQL/MariaDB database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'hack',
    'database': 'passwords_db'
}

def widget_device():
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT COUNT(*) AS total_count FROM passwords;')
        total_device = cursor.fetchone()['total_count']
        return jsonify(count=total_device)
    except Exception as e:
        # Handle exceptions, log errors, etc.
        return jsonify(error=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def widget_type():
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT COUNT(*) AS total_count FROM types;')
        total_types = cursor.fetchone()['total_count']
        return jsonify(count=total_types)
    except Exception as e:
        # Handle exceptions, log errors, etc.
        return jsonify(error=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def widget_site():
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT COUNT(*) AS total_count FROM groups;')
        total_groups = cursor.fetchone()['total_count']
        return jsonify(count=total_groups)
    except Exception as e:
        # Handle exceptions, log errors, etc.
        return jsonify(error=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def widget_jobs():
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT COUNT(*) AS total_count FROM cron_jobs;')
        total_jobs = cursor.fetchone()['total_count']
        return jsonify(count=total_jobs)
    except Exception as e:
        # Handle exceptions, log errors, etc.
        return jsonify(error=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()