import os
import requests
import random
import string
from flask import Flask, jsonify, render_template, send_from_directory

# Standard Flask initialization for Render deployment
app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def landing():
    """Serves the entrance page with the pulse sphere."""
    return render_template('landing.html')

@app.route('/generator')
def generator():
    """Serves the main engine room with the padlock visualizer."""
    return render_template('index.html')

@app.route('/generate-password')
def generate_password():
    """Proxies the ANU Lab API for true physical randomness."""
    try:
        url = 'https://qrng.anu.edu.au/API/jsonI.php?length=1&type=hex16&size=10'
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get('success'):
            return jsonify({'key': data['data'][0], 'origin': 'Quantum'})
    except:
        pass
    
    # Secure fallback using Python SystemRandom (OS Entropy)
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    fallback = ''.join(random.SystemRandom().choice(chars) for _ in range(16))
    return jsonify({'key': fallback, 'origin': 'Algorithm (Fallback)'})

# PWA Support
@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('static', 'sw.js')

if __name__ == "__main__":
    # Render binds to the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
