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

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

def widget_type():
    cursor = conn.cursor(dictionary=True)
    #cursor.execute('SELECT name, COUNT(*) as count FROM types GROUP BY name')
    cursor.execute('SELECT COUNT(*) AS total_count FROM types;')
    total_types = cursor.fetchone()['total_count']
    cursor.close()
    return jsonify(count=total_types)