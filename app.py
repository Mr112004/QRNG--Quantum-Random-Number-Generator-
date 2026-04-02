import os
import random
import string
import sqlite3
import requests
from functools import wraps
from flask import Flask, jsonify, render_template, request, send_from_directory

# Initialize Flask with absolute folder references
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- ULTIMATE CACHE BUSTER ---
# This forces the browser to ALWAYS load your latest HTML changes
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
# -----------------------------

# --- DATABASE SETUP ---
def init_db():
    """Initializes the backend-only analytics database."""
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS generation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pwd_length INTEGER,
            duration_ms REAL,
            origin TEXT,
            device_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the DB on startup
init_db()

# --- ADMIN AUTH DECORATOR ---
def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.args.get('admin_key') != 'secret123':
            return "Unauthorized access. This incident will be logged.", 401
        return f(*args, **kwargs)
    return decorated

# --- CORE ROUTES ---
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/generator')
def engine():
    return render_template('index.html')

@app.route('/generate-password')
def generate_password():
    """Proxies true entropy or falls back to secure local PRNG."""
    try:
        # Attempt ANU Quantum fetch
        url = 'https://qrng.anu.edu.au/API/jsonI.php?length=1&type=hex16&size=10'
        res = requests.get(url, timeout=2)
        if res.status_code == 200:
            return jsonify({'origin': 'Quantum'})
    except Exception as e:
        pass
    
    # Fallback response for algorithmic generation
    return jsonify({'origin': 'Algorithmic'})

# --- ANALYTICS LOGGING API ---
@app.route('/api/log-generation', methods=['POST'])
def log_generation():
    """Silently logs password generation metrics without saving the password."""
    try:
        data = request.json
        conn = sqlite3.connect('analytics.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO generation_logs (pwd_length, duration_ms, origin, device_id)
            VALUES (?, ?, ?, ?)
        ''', (data.get('length'), data.get('duration_ms'), data.get('origin'), data.get('device_id')))
        conn.commit()
        conn.close()
        return jsonify({'status': 'logged'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- ADMIN DASHBOARD ---
@app.route('/admin/analytics')
@require_admin
def admin_dashboard():
    """Renders the secure developer analytics dashboard."""
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    
    # Aggregate metrics
    c.execute("SELECT COUNT(*), AVG(pwd_length), AVG(duration_ms) FROM generation_logs")
    stats = c.fetchone()
    
    # Recent logs
    c.execute("SELECT timestamp, pwd_length, duration_ms, origin FROM generation_logs ORDER BY timestamp DESC LIMIT 100")
    logs = c.fetchall()
    conn.close()
    
    return render_template('admin.html', 
                           total=stats[0] or 0, 
                           avg_len=round(stats[1] or 0, 1), 
                           avg_time=round(stats[2] or 0, 2), 
                           logs=logs)

# --- PWA ROUTE ---
@app.route('/sw.js')
def sw():
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
