import os
from flask import Flask, jsonify, render_template, send_from_directory
import requests

app = Flask(__name__, template_folder='templates', static_folder='static')


# =========================
# ROUTING
# =========================

@app.route('/')
def landing():
    """Landing page appears first"""
    return render_template('landing.html')


@app.route('/generator')
def generator():
    """Main Quantum Key Generator page"""
    return render_template('index.html')


@app.route('/documentation')
def documentation():
    """Serve documentation file"""
    static_path = os.path.join(os.getcwd(), 'static')

    if not os.path.exists(static_path):
        os.makedirs(static_path)

    doc_file = os.path.join(static_path, 'documentation.txt')

    if not os.path.exists(doc_file):
        with open(doc_file, 'w') as f:
            f.write("QRNG - Super Quantum Documentation...")

    return send_from_directory('static', 'documentation.txt')


# =========================
# QUANTUM PASSWORD GENERATOR
# =========================

@app.route('/generate-password')
def generate_password():
    try:
        # ANU Quantum Random Number Generator API
        ANU_URL = 'https://qrng.anu.edu.au/API/jsonI.php?length=1&type=hex16&size=10'

        response = requests.get(ANU_URL, timeout=5)
        response.raise_for_status()

        data = response.json()

        if data and data.get('success') and data.get('data'):
            return jsonify({'key': data['data'][0]})

        return jsonify({'error': 'Invalid response structure'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =========================
# LOCAL DEVELOPMENT ONLY
# =========================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
