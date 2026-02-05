import sqlite3
import math
import random
import string
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "geoguard_secret_key_123" # Penting untuk session captcha
DB_NAME = "geoguard.db"

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Users Table (Menambahkan password)
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    # Locations Table
    c.execute('''CREATE TABLE IF NOT EXISTS locations 
                 (id INTEGER PRIMARY KEY, name TEXT, lat REAL, lon REAL, radius REAL)''')
    # Attendance Log
    c.execute('''CREATE TABLE IF NOT EXISTS attendance 
                 (id INTEGER PRIMARY KEY, user_id TEXT, timestamp TEXT, 
                  captured_lat REAL, captured_lon REAL, ip_address TEXT, status TEXT, distance REAL)''')
    conn.commit()
    conn.close()

# --- ROUTES BARU ---

@app.route('/api/get_captcha', methods=['GET'])
def get_captcha():
    # Generate captcha random 5 karakter
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    session['captcha'] = code
    return jsonify({"captcha": code})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username').replace("@", "")
    password = data.get('password')
    user_captcha = data.get('captcha')

    if user_captcha != session.get('captcha'):
        return jsonify({"status": "error", "message": "Captcha salah!"}), 400

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Akun berhasil dibuat! Silahkan login."})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Username sudah terdaftar!"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['user'] = username
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Username atau Password salah!"}), 401

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/attend', methods=['POST'])
def mark_attendance():
    if 'user' not in session:
        return jsonify({"status": "error", "message": "Sesi berakhir, silahkan login ulang."}), 401

    data = request.json
    user_lat = data.get('latitude')
    user_lon = data.get('longitude')
    ip_address = request.remote_addr

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM locations LIMIT 1")
    target = c.fetchone()
    
    if not target:
        return jsonify({"status": "error", "message": "Lokasi target belum diatur admin."})

    distance = calculate_distance(user_lat, user_lon, target[2], target[3])
    status = "VALID" if distance <= target[4] else "INVALID"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO attendance (user_id, timestamp, captured_lat, captured_lon, ip_address, status, distance) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (session['user'], timestamp, user_lat, user_lon, ip_address, status, distance))
    conn.commit()
    conn.close()

    return jsonify({"status": status, "message": f"Jarak: {int(distance)}m", "distance": int(distance)})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)