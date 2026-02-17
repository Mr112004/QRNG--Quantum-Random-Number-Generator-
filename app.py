import os
from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/generator')
def generator():
    return render_template('index.html')


@app.route('/generate-password')
def generate_password():
    try:
        ANU_URL = 'https://qrng.anu.edu.au/API/jsonI.php?length=1&type=hex16&size=10'
        response = requests.get(ANU_URL, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("success") and data.get("data"):
            return jsonify({"key": data["data"][0]})

        return jsonify({"error": "Invalid API response"}), 500

    except Exception:
        return jsonify({"error": "Quantum source temporarily unavailable"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
