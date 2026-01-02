from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_socketio import SocketIO, emit
import json, os
from datetime import datetime, timedelta, timezone
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "only-us-secret"
socketio = SocketIO(app)

UPLOAD_FOLDER = "uploads"
HISTORY_FILE = "chat_history.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PASSWORDS = {
    "20000608": "you",
    "20001027": "her"
}

def beijing_time():
    return (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")

if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        messages = json.load(f)
else:
    messages = []

def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pwd = request.form.get("password")
        if pwd in PASSWORDS:
            session["user"] = PASSWORDS[pwd]
            return redirect("/")
        return render_template("login.html", error="密码不对 💔")
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

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@socketio.on("connect")
def send_history():
    emit("history", messages)

@socketio.on("send_message")
def handle_message(data):
    msg = {
        "sender": session.get("user"),
        "type": data["type"],
        "content": data["content"],
        "time": beijing_time()
    }
    messages.append(msg)
    save_history()
    emit("new_message", msg, broadcast=True)

@socketio.on("send_image")
def handle_image(file):
    filename = secure_filename(file["name"])
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        f.write(file["data"])

    msg = {
        "sender": session.get("user"),
        "type": "image",
        "content": f"uploads/{filename}",
        "time": beijing_time()
    }
    messages.append(msg)
    save_history()
    emit("new_message", msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)


