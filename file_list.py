from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def list_local_directory():
    local_directory = '/root'  # Replace with the path to your local directory
    contents = list_directory_contents(local_directory)
    return render_template('index_of_local.html', local_directory=local_directory, contents=contents)

@app.route('/<path:item>')
def serve_item(item):
    item_path = os.path.join(app.config['LOCAL_DIRECTORY'], item)
    if os.path.exists(item_path):
        if os.path.isdir(item_path):
            contents = list_directory_contents(item_path)
            return render_template('index_of_local.html', local_directory=item_path, contents=contents)
        else:
            return send_from_directory(app.config['LOCAL_DIRECTORY'], item, as_attachment=True)
    else:
        return "Item not found", 404

def list_directory_contents(directory_path):
    try:
        contents = []
        for item in os.listdir(directory_path):
            full_item_path = os.path.join(directory_path, item)
            if os.path.isdir(full_item_path):
                contents.append((item + '/', True))  # Mark directories as True
            else:
                contents.append((item, False))  # Mark files as False
        return contents
    except Exception as e:
        return [str(e)]

if __name__ == '__main__':
    app.config['LOCAL_DIRECTORY'] = '/root'
    app.run(host='0.0.0.0', port=3030)

