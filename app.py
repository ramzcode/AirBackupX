from flask import Flask, render_template, send_from_directory, abort, url_for, jsonify
import os

app = Flask(__name__)

# Define your local directory here
local_directory = '/root'  # Replace with the path to your local directory

@app.route('/')
def explore_root():
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3030)
    app.debug = True

