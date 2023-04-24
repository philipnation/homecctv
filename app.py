import cv2
import datetime
import subprocess
from flask import Flask, render_template, Response

app = Flask(__name__)

#(If on linux to off system light)
# subprocess.call(["v4l2-ctl", "-c", "led1_mode=0"])

# OpenCV video capture object and video writer object
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter()
recording = False

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen():
    """Video streaming generator function."""
    while True:
        ret, frame = cap.read()
        
        if ret:
            global out, recording
            
            # Create video writer object if not already created
            if not recording:
                out.release()
                out = None
            if out is None:
                now = datetime.datetime.now()
                file_name = now.strftime("%Y-%m-%d %H-%M-%S") + ".avi"
                out = cv2.VideoWriter(file_name, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                recording = True

            # Write frame to video file
            out.write(frame)
            
            # Convert frame to JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                   
        if cv2.waitKey(1) == ord('q'):
            break
            
    # Release video capture and writer objects
    cap.release()
    out.release()
    cv2.destroyAllWindows()

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
