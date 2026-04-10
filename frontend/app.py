from flask import Flask, render_template
from waitress import serve

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def history():
    return render_template("history.html")


if __name__ == "__main__":
    print("Frontend running at http://localhost:5000")
    serve(app, host="0.0.0.0", port=5000)