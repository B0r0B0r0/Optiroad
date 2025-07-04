from flask import Flask, Response
import time
import cv2

app = Flask(__name__)
get_latest_frame_callback = None  # va fi injectat din main.py

def set_frame_callback(cb):
    global get_latest_frame_callback
    get_latest_frame_callback = cb

@app.route("/stream")
def stream():
    def generate():
        while True:
            if get_latest_frame_callback:
                frame = get_latest_frame_callback()
                if frame is not None:
                    _, buffer = cv2.imencode('.jpg', frame)
                    jpg_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n\r\n')
            time.sleep(0.05)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/health")
def health():
    print("[INFO] Health check received")
    return "ok", 200