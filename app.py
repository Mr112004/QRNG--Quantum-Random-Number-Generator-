# app.py
from flask import Flask, render_template, jsonify, send_file, make_response
import secrets
from datetime import datetime
import time
import os
import json
import math

app = Flask(__name__, static_folder='static', template_folder='templates')

# Optional: path to store the last measured bitstream (if you collect real QRNG bits)
LAST_BITS_PATH = 'static/last_bits.txt'  # simple place to write/read a cached bitstream


def bits_from_bytes(b: bytes) -> str:
    """Return a bit string (e.g. '0101...') from bytes."""
    return ''.join(f'{byte:08b}' for byte in b)


def simulated_telemetry():
    """Return simulated telemetry. Useful when no real QRNG backend connected."""
    # entropy: 0..100, bitrate qb/s, latency ms
    # simulate some time-varying values
    now = time.time()
    entropy = 55 + 40 * abs(math.sin(now / 13.0))  # pseudo-varying
    bitrate = 300 + int(200 * abs(math.cos(now / 7.0)))
    latency = 20 + int(60 * abs(math.sin(now / 5.0)))
    return {
        "entropy": round(entropy, 2),
        "bitrate": int(bitrate),
        "latency": int(latency)
    }


def get_last_bits_or_simulate(length_bits=1024):
    """
    Return a bitstring for the frontend to optionally use.
    - If LAST_BITS_PATH exists and has bits, read it.
    - Else generate cryptographically-random bits locally (not quantum).
    """
    # If a real QRNG pipeline writes LAST_BITS_PATH, prefer that
    if os.path.exists(LAST_BITS_PATH):
        try:
            with open(LAST_BITS_PATH, 'r') as f:
                s = f.read().strip()
                # Basic sanity: ensure it only contains 0/1 and has some length
                if len(s) >= 64 and set(s) <= {'0', '1'}:
                    return s
        except Exception:
            pass

    # fallback: produce secure random bytes and convert to bitstring
    b = secrets.token_bytes(max(16, length_bits // 8))  # token_bytes(length in bytes)
    return bits_from_bytes(b)[:length_bits]


@app.route('/')
def index():
    # render templates/index.html
    return render_template('index.html')


@app.route('/generate-password')
def generate_password():
    """
    Simple endpoint that returns a generated token as JSON.
    The front-end will apply its charset & length logic, but we keep this for compatibility.
    """
    # Generate a secure random 64-hex-character string (32 bytes)
    key = secrets.token_hex(32)
    timestamp = datetime.utcnow().isoformat() + "Z"
    return jsonify({"key": key, "timestamp": timestamp})


@app.route('/qrng-stats')
def qrng_stats():
    """
    Endpoint consumed by the frontend visualizer.
    Returns JSON with:
      - entropy: float (0..100)
      - bitrate: int (qb/s)
      - latency: int (ms)
      - bits: optional string containing '0'/'1' characters (short or long)
    """
    # === Option A: if you have a real backend, plug it here ===
    # Example pseudo:
    # try:
    #     data = query_your_qrng_service()
    #     return jsonify(data)
    # except Exception:
    #     pass
    # =========================================================

    # For now return simulated telemetry and an optional bitstream
    telemetry = simulated_telemetry()

    # Provide bits if you want the front-end to consume them.
    # Keep the bitstring moderately sized (e.g., 2048 bits) to avoid huge payloads.
    bits = get_last_bits_or_simulate(length_bits=2048)

    resp = {
        "entropy": telemetry["entropy"],
        "bitrate": telemetry["bitrate"],
        "latency": telemetry["latency"],
        "bits": bits
    }
    # Add server timestamp (useful for debugging)
    resp["server_time"] = datetime.utcnow().isoformat() + "Z"
    return jsonify(resp)


@app.route('/download-bits')
def download_bits():
    """
    Optional helper: download the last generated bitstream as a .txt file.
    - This reads LAST_BITS_PATH if present, otherwise generates bits on the fly.
    """
    bits = ''
    if os.path.exists(LAST_BITS_PATH):
        try:
            with open(LAST_BITS_PATH, 'r') as f:
                bits = f.read().strip()
        except Exception:
            bits = ''
    if not bits:
        bits = get_last_bits_or_simulate(4096)

    # Build a response that triggers download
    r = make_response(bits)
    r.headers['Content-Type'] = 'text/plain; charset=utf-8'
    r.headers['Content-Disposition'] = 'attachment; filename=qrng_bits.txt'
    return r


# === Example helper: how to save a real bitstream (call this from your QRNG/IBM job handler) ===
def save_last_bits(bitstring: str):
    """Save a bitstring to LAST_BITS_PATH (atomic-ish)."""
    try:
        tmp = LAST_BITS_PATH + '.tmp'
        with open(tmp, 'w') as f:
            f.write(bitstring)
        os.replace(tmp, LAST_BITS_PATH)
        return True
    except Exception:
        return False


if __name__ == '__main__':
    # Run locally on port 5000 (development). Use a production WSGI server for deployment.
    app.run(host='0.0.0.0', port=5000, debug=True)
