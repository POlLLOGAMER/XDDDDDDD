from flask import Flask, Response
app = Flask(__name__)

def generate():
    with open("rickroll.mp4", "rb") as f:
        chunk = f.read(1024*1024)
        while chunk:
            yield chunk
            chunk = f.read(1024*1024)

@app.route("/video")
def video():
    return Response(generate(), mimetype="video/mp4")

@app.route("/")
def index():
    return '<video src="/video" autoplay loop muted style="width:100vw;height:100vh;"></video>'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
