from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit
import os
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "only-us-secret-key"
socketio = SocketIO(app)

PASSWORDS = {
    "20000608": "you",
    "20001027": "her"
}

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- 时间（北京时间） ----------
def beijing_time():
    return (datetime.utcnow() + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")

# ---------- SQLite 工具 ----------
def get_db():
    conn = sqlite3.connect("chat.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_messages():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT sender, type, content, time FROM messages ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_message(sender, msg_type, content, time):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (sender, type, content, time) VALUES (?, ?, ?, ?)",
        (sender, msg_type, content, time)
    )
    conn.commit()
    conn.close()

# ---------- 路由 ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pwd = request.form.get("password")
        if pwd in PASSWORDS:
            session["user"] = PASSWORDS[pwd]
            return redirect("/")
        return render_template("login.html", error="密码不对哦 💔")
    return render_template("login.html")

@app.route("/")
def chat():
    if "user" not in session:
        return redirect("/login")
    return render_template("chat.html", user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- Socket.IO ----------
@socketio.on("connect")
def send_history():
    history = fetch_messages()
    emit("history", history)

@socketio.on("send_message")
def handle_message(data):
    sender = session.get("user")
    time = beijing_time()
    content = data["content"]

    save_message(sender, "text", content, time)

    emit("new_message", {
        "sender": sender,
        "type": "text",
        "content": content,
        "time": time
    }, broadcast=True)

@socketio.on("send_image")
def handle_image(data):
    sender = session.get("user")
    time = beijing_time()

    filename = time.replace("/", "").replace(":", "").replace(" ", "") + "_" + data["name"]
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        f.write(data["data"])

    img_path = f"static/uploads/{filename}"
    save_message(sender, "image", img_path, time)

    emit("new_message", {
        "sender": sender,
        "type": "image",
        "content": img_path,
        "time": time
    }, broadcast=True)

# ---------- 启动 ----------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)





