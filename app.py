import os
import sqlite3
import traceback
import requests
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

KANBAN_DB = '/opt/data/kanban.db'
KANBAN_API_URL = os.getenv('KANBAN_API_URL', '').strip()
BOARD = os.getenv('KANBAN_BOARD', 'default')
PROFILE = os.getenv('KANBAN_PROFILE', '')

def db_conn():
    db_path = os.getenv('KANBAN_DB', KANBAN_DB)
    candidates = [
        db_path,
        '/opt/data/kanban.db',
        '/data/kanban.db',
        '/app/kanban.db'
    ]
    chosen = None
    for path in candidates:
        if os.path.isfile(path):
            chosen = path
            break
    if not chosen:
        raise FileNotFoundError(f'Kanban DB not found in candidates: {candidates}')
    # Use read-only URI to avoid write issues on read-only mounts
    # SQLite read-only mode requires file URI
    try:
        uri = f'file:{chosen}?mode=ro&cache=shared'
        conn = sqlite3.connect(uri, uri=True, check_same_thread=False, timeout=30)
        return conn
    except Exception:
        # fallback to regular connect
        return sqlite3.connect(chosen, check_same_thread=False, timeout=30)

@app.route('/api/stats')
def stats():
    profile = request.args.get('profile', PROFILE)
    if KANBAN_API_URL:
        try:
            r = requests.get(f"{KANBAN_API_URL}/stats", params={'profile': profile} if profile else {}, timeout=10)
            r.raise_for_status()
            return jsonify(r.json())
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    try:
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
        cur.execute("SELECT assignee, COUNT(*) FROM tasks GROUP BY assignee")
        assignees = cur.fetchall()
        conn.close()
        return jsonify({
            'by_status': {s:c for s,c in rows},
            'by_assignee': {a:c for a,c in assignees if a}
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks')
def tasks():
    profile = request.args.get('profile', PROFILE)
    status = request.args.get('status', '')
    if KANBAN_API_URL:
        try:
            params = {}
            if profile: params['profile'] = profile
            if status: params['status'] = status
            params['limit'] = request.args.get('limit','200')
            r = requests.get(f"{KANBAN_API_URL}/tasks", params=params, timeout=10)
            r.raise_for_status()
            return jsonify(r.json())
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    try:
        limit = int(request.args.get('limit','200'))
    except:
        limit = 200
    try:
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
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    db_path = os.getenv('KANBAN_DB', KANBAN_DB)
    exists = os.path.exists(db_path)
    size = os.path.getsize(db_path) if exists else 0
    tables = []
    try:
        conn = db_conn()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
    except Exception as e:
        tables = [f'error: {e}']
    return jsonify({
        'db_path': db_path,
        'exists': exists,
        'size': size,
        'tables': tables
    })

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT',5000)), debug=False)
