import cv2
from flask import Flask, Response

app = Flask(__name__)

# Initializing the video from the default camera indexed at 0.
# We can specify a different camera index if we have multiple cameras connected.)
video_capture = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            # Encode the frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/') #root route url stating about the project
def index():
    return "<center><h1>Ultra-Low latency Video and Signal Streaming Platform;</h1><h2>Assignment for SDE role by Sir Lokesh Reddy @ControlOne.ai</h2>"

@app.route('/video_feed') #returns the video feed in a said boundry
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__": #starting the application
    app.run(host='0.0.0.0', port=3000)
