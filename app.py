from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "only-us-secret-key"  # 随便写，但别给别人看

PASSWORD = "20250415"  # ← 改成你们的暗号

messages = []

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pwd = request.form.get("password")
        if pwd == PASSWORD:
            session["auth"] = True
            return redirect("/")
        else:
            return render_template("login.html", error="密码不对哦 💔")
    return render_template("login.html")

@app.route("/", methods=["GET", "POST"])
def chat():
    if not session.get("auth"):
        return redirect("/login")

    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            messages.append(msg)
        return redirect("/")

    return render_template("chat.html", messages=messages)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

