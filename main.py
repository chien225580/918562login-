import os
import json
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

DATA_FILE = "users.json"
PORT = int(os.environ.get("PORT", 3000))

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_users():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/")
def home():
    return "Render Server Online"

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    phone = data.get("phone", "").strip()

    if not username or not password or not phone:
        return jsonify({"success": False, "msg": "Thiếu thông tin"})

    users = load_users()

    for u in users:
        if u["username"] == username:
            return jsonify({"success": False, "msg": "Tên đã tồn tại"})
        if u["phone"] == phone:
            return jsonify({"success": False, "msg": "SĐT đã tồn tại"})

    users.append({
        "username": username,
        "password": hash_password(password),
        "phone": phone
    })

    save_users(users)
    return jsonify({"success": True, "msg": "Đăng ký thành công"})

app.run(host="0.0.0.0", port=PORT)
