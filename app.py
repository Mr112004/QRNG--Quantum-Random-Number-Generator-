import string
import os
from flask import Flask, jsonify, render_template, send_from_directory
import requests 
import sys 

app = Flask(__name__)

# --- ROUTING ---

@app.route('/')
def landing():
    """Serves the new interactive landing page first."""
    return render_template('landing.html')

@app.route('/generator')
def index():
    """Serves the main Quantum Key Engine."""
    return render_template('index.html')

@app.route('/documentation')
def documentation():
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('static/documentation.txt'):
        with open('static/documentation.txt', 'w') as f:
            f.write("QRNG - Super Quantum Documentation...")
    return send_from_directory('static', 'documentation.txt')

@app.route('/generate-password')
def generate_password():
    try:
        # ANU API Proxy
        ANU_URL = 'https://qrng.anu.edu.au/API/jsonI.php?length=1&type=hex16&size=10'
        response = requests.get(ANU_URL, timeout=5) 
        response.raise_for_status() 
        data = response.json()
        
        if data and data.get('success') and data.get('data'):
            return jsonify({'key': data['data'][0]})
        return jsonify({'error': 'Invalid structure'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
