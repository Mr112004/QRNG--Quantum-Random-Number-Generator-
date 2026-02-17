import os
import requests
import random
import string
from flask import Flask, jsonify, render_template, send_from_directory

# Initialize Flask with specific template and static targets
app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def landing():
    """Serves the cinematic landing page first."""
    return render_template('landing.html')

@app.route('/generator')
def generator():
    """Serves the main Quantum Engine room."""
    return render_template('index.html')

@app.route('/generate-password')
def generate_password():
    """Fetches real-time entropy from the ANU Quantum Lab."""
    try:
        # Requesting 10-byte hex randomness from ANU
        url = 'https://qrng.anu.edu.au/API/jsonI.php?length=1&type=hex16&size=10'
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data and data.get('success'):
            return jsonify({'key': data['data'][0], 'origin': 'Quantum (Physical)'})
    except Exception:
        pass
    
    # Secure PRNG Fallback if Lab is unreachable
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    fallback = ''.join(random.SystemRandom().choice(chars) for _ in range(16))
    return jsonify({'key': fallback, 'origin': 'Algorithm (Fallback)'})

# PWA Support routes
@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('static', 'sw.js')

if __name__ == "__main__":
    # Render environment port handling
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
