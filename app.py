import os
import subprocess
import json
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

HERMES_BIN = '/opt/hermes/bin/hermes'
HERMES_HOME = '/opt/data/profiles/andre'
BOARD = os.getenv('KANBAN_BOARD', 'default')

def run_hermes(args):
    env = os.environ.copy()
    env['HERMES_HOME'] = HERMES_HOME
    cmd = [HERMES_BIN, 'kanban'] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return result.stdout, result.stderr, result.returncode

@app.route('/api/stats')
def stats():
    stdout, stderr, code = run_hermes(['--board', BOARD, 'stats'])
    # simple parse
    data = {'raw': stdout}
    return jsonify(data)

@app.route('/api/tasks')
def tasks():
    stdout, stderr, code = run_hermes(['--board', BOARD, 'list'])
    lines = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # format: ✓ t_id  status  assignee  title...
        parts = line.split(None, 3)
        if len(parts) >= 4:
            icon, tid, status, rest = parts
            # rest contains assignee and title? Actually list output format is different
            # We'll return raw
            lines.append(line)
    return jsonify({'raw': stdout, 'lines': lines})

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
