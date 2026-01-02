from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)

messages = []

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            messages.append(msg)
        return redirect("/")
    return render_template("chat.html", messages=messages)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
