import os
import json
import time
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# 🔐 Bật CORS cho mọi origin
CORS(app, resources={r"/*": {"origins": "*"}})

DATA_FILE = "users.json"
PORT = int(os.environ.get("PORT", 3000))

# ⏱ Chống spam đăng ký
LAST_REQUEST = {}
REQUEST_DELAY = 5  # giây

# 🔑 Khoá admin (ĐỔI CHUỖI NÀY)
ADMIN_KEY = "12131415"

# ------------------ UTILS ------------------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def load_users():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return "Render Server Online"

# 🔄 Ping giữ server sống
@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "time": int(time.time())})

# 📝 Đăng ký
@app.route("/register", methods=["POST"])
def register():
    ip = client_ip()
    now = time.time()

    # 🚫 Chống spam
    if ip in LAST_REQUEST and now - LAST_REQUEST[ip] < REQUEST_DELAY:
        return jsonify({
            "success": False,
            "msg": "Vui lòng thao tác chậm lại"
        })

    LAST_REQUEST[ip] = now

    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success": False,
            "msg": "Dữ liệu không hợp lệ"
        })

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    phone = data.get("phone", "").strip()

    # ❌ Thiếu thông tin
    if not username or not password or not phone:
        return jsonify({
            "success": False,
            "msg": "Chưa điền đủ thông tin"
        })

    users = load_users()

    # ❌ Trùng tên / SĐT
    for u in users:
        if u["username"] == username:
            return jsonify({
                "success": False,
                "msg": "Tên đăng ký đã tồn tại"
            })
        if u["phone"] == phone:
            return jsonify({
                "success": False,
                "msg": "Số điện thoại đã tồn tại"
            })

    # ✅ Đăng ký thành công
    users.append({
        "username": username,
        "password": hash_password(password),
        "phone": phone,
        "created_at": int(time.time())
    })

    save_users(users)

    return jsonify({
        "success": True,
        "msg": "Đăng ký thành công"
    })

# 👮 ADMIN XEM USER (MIỄN PHÍ – KHÔNG CẦN SHELL)
@app.route("/admin/users", methods=["GET"])
def admin_users():
    key = request.args.get("key")

    if key != ADMIN_KEY:
        return jsonify({
            "success": False,
            "msg": "Không có quyền truy cập"
        })

    users = load_users()

    # Ẩn mật khẩu khi trả về
    safe_users = []
    for u in users:
        safe_users.append({
            "username": u["username"],
            "phone": u["phone"],
            "created_at": u["created_at"]
        })

    return jsonify({
        "success": True,
        "total": len(safe_users),
        "users": safe_users
    })

# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
