from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_socketio import SocketIO, emit
import json, os
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
app.secret_key = "only-us-secret-key"
socketio = SocketIO(app)

PASSWORDS = {
    "20000608": "you",
    "20001027": "her"
}

HISTORY_FILE = "chat_history.json"
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def beijing_time():
    return (datetime.utcnow() + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(msgs):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(msgs, f, ensure_ascii=False, indent=2)

messages = load_history()

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

@socketio.on("connect")
def send_history():
    emit("history", messages)

@socketio.on("send_message")
def handle_message(data):
    msg = {
        "sender": session.get("user"),
        "type": "text",
        "content": data["content"],
        "time": beijing_time()
    }
    messages.append(msg)
    save_history(messages)
    emit("new_message", msg, broadcast=True)

@socketio.on("send_image")
def handle_image(data):
    filename = beijing_time().replace("/", "").replace(":", "").replace(" ", "") + "_" + data["name"]
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(data["data"])

    msg = {
        "sender": session.get("user"),
        "type": "image",
        "content": f"static/uploads/{filename}",
        "time": beijing_time()
    }
    messages.append(msg)
    save_history(messages)
    emit("new_message", msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)



