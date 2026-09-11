from flask import Flask, render_template

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/hello")
def hello():
    return {
        "message": "Hello from Python",
        "author": "Duc"
    }

if __name__ == "__main__":
    app.run(debug=True, port=8000)