import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

KANBAN_DB = '/opt/data/kanban.db'

def db_conn():
    return sqlite3.connect(KANBAN_DB, check_same_thread=False, timeout=30)

@app.route('/stats')
def stats():
    profile = request.args.get('profile')
    conn = db_conn()
    cur = conn.cursor()
    if profile:
        cur.execute("SELECT status, COUNT(*) FROM tasks WHERE assignee=? GROUP BY status", (profile,))
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

@app.route('/tasks')
def tasks():
    profile = request.args.get('profile')
    status = request.args.get('status')
    limit = int(request.args.get('limit','200'))
    conn = db_conn()
    cur = conn.cursor()
    if profile and status:
        cur.execute("SELECT id,title,status,assignee,created_at,completed_at FROM tasks WHERE assignee=? AND status=? ORDER BY created_at DESC LIMIT ?", (profile,status,limit))
    elif profile:
        cur.execute("SELECT id,title,status,assignee,created_at,completed_at FROM tasks WHERE assignee=? ORDER BY created_at DESC LIMIT ?", (profile,limit))
    elif status:
        cur.execute("SELECT id,title,status,assignee,created_at,completed_at FROM tasks WHERE status=? ORDER BY created_at DESC LIMIT ?", (status,limit))
    else:
        cur.execute("SELECT id,title,status,assignee,created_at,completed_at FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return jsonify({'tasks': [{'id':r[0],'title':r[1],'status':r[2],'assignee':r[3],'created_at':r[4],'completed_at':r[5]} for r in rows]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
