import os
import requests
import random
import string
from flask import Flask, jsonify, render_template, send_from_directory

# Initialize Flask with absolute folder references
app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def landing():
    """Serves the cinematic entrance."""
    return render_template('landing.html')

@app.route('/generator')
def generator():
    """Serves the main engine room."""
    return render_template('index.html')

@app.route('/generate-password')
def generate_password():
    """Proxies true entropy or falls back to secure local PRNG."""
    try:
        url = 'https://qrng.anu.edu.au/API/jsonI.php?length=1&type=hex16&size=10'
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get('success'):
            return jsonify({'key': data['data'][0], 'origin': 'Quantum'})
    except:
        pass
    
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    fallback = ''.join(random.SystemRandom().choice(chars) for _ in range(16))
    return jsonify({'key': fallback, 'origin': 'Algorithm'})

# --- CRITICAL PWA ROUTE FIX ---
# Serving sw.js from root /sw.js instead of /static/sw.js to allow root scope control
@app.route('/sw.js')
def serve_sw():
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
