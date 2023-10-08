import cv2
import requests
import numpy as np
from flask import Flask, render_template, Response, request, jsonify

app = Flask(__name__)

# URLs of the video feeds provided by the host computer
video_feed_url_1 = 'http://192.168.1.104:3000/video_feed' #you needa change the url according to the sender machine
video_feed_url_2 = 'http://192.168.1.104:3000/video_feed' #you needa change the url according to the sender machine

# ALl Signal Dictionary
signals = {
    "Gas": False,
    "Brake": False,
    "Left": False,
    "Right": False,
    "Levitate": False,
    "Descend": False
}

def get_frame(url):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        bytes_data = bytes()
        for chunk in response.iter_content(chunk_size=1024):
            bytes_data += chunk
            a = bytes_data.find(b'\xff\xd8')
            b = bytes_data.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                yield frame

@app.route('/') #Defined the root route to render an HTML template:
def index():
    return render_template('index.html', signals=signals)

def generate_frames_1():
    for frame in get_frame(video_feed_url_1):
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frame)[1].tobytes() + b'\r\n')

def generate_frames_2():
    for frame in get_frame(video_feed_url_2):
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frame)[1].tobytes() + b'\r\n')

@app.route('/video_feed_1')
def video_feed_1():
    return Response(generate_frames_1(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_2')
def video_feed_2():
    return Response(generate_frames_2(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/update_signal', methods=['POST'])
def update_signal():
    global signals
    data = request.get_json()
    for key in signals:
        if key in data:
            signals[key] = data[key]
            if data[key]:
                print(f"Button Pressed: {key}") #gets updates on which button pressed; this can be used later to 
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)#start app on port 4000
