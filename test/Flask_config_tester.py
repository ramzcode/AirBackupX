# app.py
from flask import Flask, render_template, request, redirect
import json
from config import CONFIG

app = Flask(__name__)

# Inside your Flask route
@app.route('/')
def index():
    section_selected = request.args.get('section', 'section1')  # Default to section1 if not provided
    selected_section_keys = CONFIG.get(section_selected, {}).keys()  # Get keys of the selected section or an empty list if not found
    return render_template('index.html', config=CONFIG, section_selected=section_selected, selected_section_keys=selected_section_keys)

@app.route('/update', methods=['POST'])
def update_config():
    section = request.form['section']
    key = request.form['key']
    new_value = request.form['new_value']

    # Read the existing Python configuration file
    with open('config.py', 'r') as py_file:
        python_code = py_file.read()

    # Extract CONFIG dictionary from the Python code
    exec(python_code, globals())
    config_data = globals().get('CONFIG', {})

    # Update the nested configuration
    config_data[section][key] = new_value

    # Convert the updated dictionary to JSON format
    json_config = json.dumps(config_data, indent=4)

    # Write the updated JSON data back to the Python configuration file
    with open('config.py', 'w') as py_file:
        py_file.write(f'CONFIG = {json_config}')

    return redirect('/')

if __name__ == '__main__':
   # app.run(debug=True)
    app.run(host='0.0.0.0', port=3030)

