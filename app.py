from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, Response, session
from werkzeug.utils import secure_filename

import numpy as np
import cv2
import os
import shutil
from ultralytics import YOLO
import re

from utils import detect_sample_model
from utils import add_bboxs_on_img
from utils import object_json


#Setup cấu hình cho camera
start_camera = 0
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


#Gọi model
model = YOLO("models/best.pt")

#Tạo Flask app
app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
ALLOW_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
pattern_name = r'^(\w+)'
app.secret_key = "trannhancoder"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.'in filename and filename.rsplit('.', 1)[1].lower() in ALLOW_EXTENSIONS


@app.route('/')
def home():
    if str(session.get('on_cam')) == "1":
        session['on_cam'] = "0"
        cap.release()
    return render_template("index.html")


@app.route('/', methods=["POST"])
def upload_image():
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        
        filename = secure_filename(file.filename)
        if os.path.isdir("static/uploads"):
            shutil.rmtree("static/uploads")
        os.mkdir("static/uploads")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash("Image Successfully Uploaded, Display And Predict Below")
        
        input_image = cv2.imread("./static/uploads/{}".format(filename))
        # model predict
        predict = detect_sample_model(input_image)

        # add bbox on image
        final_image = add_bboxs_on_img(image = input_image, predict = predict)
        
        image = cv2.cvtColor(np.array(final_image), cv2.COLOR_RGB2BGR)
        image = cv2.resize(image[:,:,::-1], (640, 480))
        
        name_image = re.findall(pattern_name, filename)
        
        cv2.imwrite("static/uploads/{}_predict.jpg".format(name_image[0]), image)
        
        filename = "{}_predict.jpg".format(name_image[0])
        
        return render_template('index.html', filename=filename)
    else:
        flash("Allowed image types are - png, jpg, jpeg")
        return redirect(request.url)
    

@app.route('/display/<filename>')
def display_images(filename):
    
    return redirect(url_for("static", filename="uploads/" + filename))


def get_prediction(input_image):
     
    predict = detect_sample_model(input_image)
    # add bbox on image
    final_image = add_bboxs_on_img(image = input_image, predict = predict)
    
    image = cv2.cvtColor(np.array(final_image), cv2.COLOR_RGB2BGR)
    
    image = cv2.resize(image[:,:,::-1], (640, 480))
    
    return image


@app.route('/camera')
def camera():
    global cap
    if str(session.get('on_cam')) == "0":
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    session['on_cam'] = "1"
    
    return render_template("camera.html")


def generate_frames_camera():
    while True:
        success, frame = cap.read()

        if not success:
            break
        else:
            frame = get_prediction(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            
@app.route('/video_feed_camera')
def video_feed_camera():
    return Response(generate_frames_camera(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/camera', methods=["POST"])
def start_or_stop():
    global start_camera
    global cap
    if start_camera == 0:
        start_camera = 1
        cap.release()
        cv2.destroyAllWindows()
    else:
        cap = cv2.VideoCapture(0)
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        start_camera = 0
    return render_template('camera.html')


@app.route('/video')
def video():
    if str(session.get('on_cam')) == "1":
        session['on_cam'] = "0"
        cap.release()
    return render_template('video.html')

@app.route('/upload_video', methods=['GET', 'POST'])
def upload_video():
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    session['filename'] = filename
    if os.path.isdir("static/uploads"):
        
        shutil.rmtree("static/uploads")
        
    os.mkdir("static/uploads")
    
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    return render_template('predict_video.html', filename=filename)


def generate_frames_video(filename):
    
    if os.path.isdir("static/result"):
        shutil.rmtree("static/result")
    os.mkdir("static/result")
    video = cv2.VideoCapture("static/uploads/" + filename)
    while True:
        success, frame = video.read()
        if not success:
            break
        else:
            frame = cv2.resize(frame, (640, 480))

            frame = get_prediction(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            
@app.route('/video_feed_video')
def video_feed_video():
    
    filename = session.get('filename')
    
    return Response(generate_frames_video(filename), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug = True)