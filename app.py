from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit
import os, json, base64
from datetime import datetime
from zoneinfo import ZoneInfo
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "only-us-secret-key"
socketio = SocketIO(app, cors_allowed_origins="*")

# 密码
PASSWORD_ME = "20000608"
PASSWORD_HER = "20001027"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HISTORY_FILE = "chat_history.json"


def now_beijing():
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y/%m/%d %H:%M")


def load_messages():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_messages(msgs):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(msgs, f, ensure_ascii=False, indent=2)


messages = load_messages()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pwd = request.form.get("password")
        if pwd == PASSWORD_ME:
            session["user"] = "你"
            return redirect("/")
        elif pwd == PASSWORD_HER:
            session["user"] = "她"
            return redirect("/")
        else:
            return render_template("login.html", error="密码不对 💔")
    return render_template("login.html")


@app.route("/")
def chat():
    if "user" not in session:
        return redirect("/login")
    return render_template("chat.html", user=session["user"], messages=messages)


@socketio.on("send_text")
def handle_text(data):
    msg = {
        "sender": data["sender"],
        "type": "text",
        "content": data["content"],
        "time": now_beijing()
    }
    messages.append(msg)
    save_messages(messages)
    emit("new_message", msg, broadcast=True)


@socketio.on("send_image")
def handle_image(data):
    sender = data["sender"]
    filename = secure_filename(data["filename"])
    image_base64 = data["data"].split(",")[1]

    image_bytes = base64.b64decode(image_base64)
    path = os.path.join(UPLOAD_FOLDER, filename)

    with open(path, "wb") as f:
        f.write(image_bytes)

    msg = {
        "sender": sender,
        "type": "image",
        "content": path,
        "time": now_beijing()
    }
    messages.append(msg)
    save_messages(messages)
    emit("new_message", msg, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)



