import os
import sqlite3
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

KANBAN_DB = '/opt/data/kanban.db'
BOARD = os.getenv('KANBAN_BOARD', 'default')
PROFILE = os.getenv('KANBAN_PROFILE', '')

def db_conn():
    return sqlite3.connect(KANBAN_DB)

@app.route('/api/stats')
def stats():
    profile = request.args.get('profile', PROFILE)
    conn = db_conn()
    cur = conn.cursor()
    if profile:
        cur.execute("""
            SELECT status, COUNT(*) FROM tasks
            WHERE assignee = ? GROUP BY status
        """, (profile,))
    else:
        cur.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    rows = cur.fetchall()
    # also per assignee
    cur.execute("SELECT assignee, COUNT(*) FROM tasks GROUP BY assignee")
    assignees = cur.fetchall()
    conn.close()
    return jsonify({
        'by_status': {s:c for s,c in rows},
        'by_assignee': {a:c for a,c in assignees if a}
    })

@app.route('/api/tasks')
def tasks():
    profile = request.args.get('profile', PROFILE)
    status = request.args.get('status', '')
    limit = int(request.args.get('limit','200'))
    conn = db_conn()
    cur = conn.cursor()
    if profile and status:
        cur.execute("""
            SELECT id, title, status, assignee, created_at, completed_at
            FROM tasks WHERE assignee=? AND status=? ORDER BY created_at DESC LIMIT ?
        """, (profile, status, limit))
    elif profile:
        cur.execute("""
            SELECT id, title, status, assignee, created_at, completed_at
            FROM tasks WHERE assignee=? ORDER BY created_at DESC LIMIT ?
        """, (profile, limit))
    elif status:
        cur.execute("""
            SELECT id, title, status, assignee, created_at, completed_at
            FROM tasks WHERE status=? ORDER BY created_at DESC LIMIT ?
        """, (status, limit))
    else:
        cur.execute("""
            SELECT id, title, status, assignee, created_at, completed_at
            FROM tasks ORDER BY created_at DESC LIMIT ?
        """, (limit,))
    rows = cur.fetchall()
    conn.close()
    tasks_list = [{
        'id': r[0],
        'title': r[1],
        'status': r[2],
        'assignee': r[3],
        'created_at': r[4],
        'completed_at': r[5]
    } for r in rows]
    return jsonify({'tasks': tasks_list, 'profile': profile or None})

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
