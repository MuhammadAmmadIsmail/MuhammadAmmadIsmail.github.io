from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
from datetime import datetime
import re
import json

app = Flask(__name__, static_folder='.', static_url_path='/')

MESSAGE_DIR = Path(__file__).resolve().parent / 'messages'
MESSAGE_DIR.mkdir(exist_ok=True)

def safe_filename(value: str) -> str:
    return re.sub(r'[^A-Za-z0-9_-]', '_', value).strip('_')[:40]

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/projects.json')
def serve_projects():
    try:
        with open('projects.json', 'r', encoding='utf-8') as f:
            projects = json.load(f)
        return jsonify(projects)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not message:
        return jsonify({'status': 'error', 'message': 'Please provide name, email, and message.'}), 400

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{safe_filename(name)}.txt"
    file_path = MESSAGE_DIR / filename

    with file_path.open('w', encoding='utf-8') as file:
        file.write(f'Name: {name}\n')
        file.write(f'Email: {email}\n')
        file.write(f'Time: {datetime.utcnow().isoformat()}Z\n')
        file.write('\nMessage:\n')
        file.write(message)

    return jsonify({'status': 'success', 'message': 'Message received — thank you! I will follow up soon.'})

if __name__ == '__main__':
    app.run(debug=True)
