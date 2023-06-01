from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, Response, session
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin

import numpy as np
import cv2
import os
import shutil
from ultralytics import YOLO
import re
import json
from PIL import Image
import io
import requests
from threading import Thread
from flask_restful import Api, Resource
from data.db import *


from utils import detect_sample_model, add_bboxs_on_img, object_json, save_object, get_prediction, get_parameters, get_average

dangerous_str = ""
user_id = ""

#Gọi model
model = YOLO("models/best.pt")

#Tạo Flask app
app = Flask(__name__)
api = Api(app)
# CORS(app, support_credentials=True)
# CORS(app, origins='http://localhost:4200')
CORS(app, supports_credentials=True, origins='http://localhost:4200')

UPLOAD_FOLDER = "static/uploads"
ALLOW_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
pattern_name = r'^(\w+)'
app.secret_key = "trannhancoder"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Setup cấu hình cho camera
start_camera = 0
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 700)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

## Login , Logout
conn = connect()

class User:
    def __init__(self, HoTen, TenDN, DiaChi, NgaySinh, MatKhau):
        self.HoTen = HoTen
        self.TenDN = TenDN
        self.DiaChi = DiaChi
        self.NgaySinh = NgaySinh
        self.MatKhau = MatKhau

@app.route("/login", methods=["POST"])
async def login_user():
    global user_id
    user = request.form.get("user")
    password = request.form.get("password")
    results = Login(conn, user, password)
    if not results:
        return {"error": f"User with this id {id} does not exist"}, 404
    print("-------->{}".format(results['UserID']))
    user_id= results['UserID']
    return  results

@app.route("/delete_result_by_id/<id>", methods=["DELETE"])
async def delete_result_by_id(id):
    results = delete_result_by_id(conn, id)
    return results

@app.route("/get/<id>", methods=["GET"])
async def get_user(id):
    user = get_user_by_id(conn, id)
    results = get_average(user)
    return results

@app.route("/user", methods=["POST"])
async def insert_user():
    HoTen = request.form.get("HoTen")
    TenDN = request.form.get("TenDN")
    DiaChi = request.form.get("DiaChi")
    NgaySinh = request.form.get("NgaySinh")
    MatKhau = request.form.get("MatKhau")
    insert_user(conn, HoTen, TenDN, DiaChi, NgaySinh, MatKhau)
    return {
        "HoTen": HoTen,
        "TenDN": TenDN,
        "DiaChi": DiaChi,
        "NgaySinh" : NgaySinh,
        "MatKhau" : MatKhau,
    }
    
@app.route("/update_user/<UserID>", methods=["PUT"])
async def update_user(UserID):
    HoTen = request.form.get("HoTen")
    TenDN = request.form.get("TenDN")
    DiaChi = request.form.get("DiaChi")
    NgaySinh = request.form.get("NgaySinh")
    MatKhau = request.form.get("MatKhau")
    update_table_users(conn, UserID, HoTen, TenDN, DiaChi, NgaySinh, MatKhau)
    return {
        "UserID": UserID,
        "HoTen": HoTen,
        "TenDN": TenDN,
        "DiaChi": DiaChi,
        "NgaySinh" : NgaySinh,
        "MatKhau" : MatKhau,
    }


def allowed_file(filename):
    return '.'in filename and filename.rsplit('.', 1)[1].lower() in ALLOW_EXTENSIONS

def generate_frames_camera():
    global user_id
    global dangerous_str
    while True:
        success, frame = cap.read()

        if not success:
            break
        else:
            thread = Thread(target=get_prediction, args=(frame,))
            thread.start()
            thread.join()
            frame, dangerous = get_prediction(frame)
            save_object(frame)
            get_parameters(conn, image = frame, user_id= user_id)
            dangerous_str = ' '.join(dangerous)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
def generate_frames_video(video):
    global user_id
    global dangerous_str
    while True:
        success, frame = video.read()
        if not success:
            break
        else:
            # frame = cv2.resize(frame, (640, 480))
            thread = Thread(target=get_prediction, args=(frame,))
            thread.start()
            thread.join()
            frame, dangerous = get_prediction(frame)
            save_object(frame)
            get_parameters(conn, image = frame, user_id= user_id)
            dangerous_str = ' '.join(dangerous)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            


@app.route('/')
async def home():
    if str(session.get('on_cam')) == "1":
        session['on_cam'] = "0"
        cap.release()
    return render_template("index.html")


@app.route('/', methods=["POST"])
async def upload_image():
    global user_id
    
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
        thread = Thread(target=detect_sample_model, args=(input_image,))
        thread.start()
        thread.join()
        save_object(input_image)
        predict = detect_sample_model(input_image)

        # classes = predict[]
        file_path = "./static/uploads/{}".format(filename)
        resp = requests.post("http://localhost:5000/predict",
                             files={"file": open(file_path, 'rb')})
        
        data = json.loads(resp.text)
        
        result = data['result']
        dangerous = []

        objects_detect = result["detect_objects_names"].replace(" ", "").split(',')
        if 'NO-SafetyVest' in objects_detect:
            dangerous.append('NO-Safety Vest')
        if 'NO-Hardhat' in objects_detect:
            dangerous.append('NO-Hardhat')
        if "NO-Mask" in objects_detect:
            dangerous.append("NO-Mask")

        get_parameters(conn, image = input_image, user_id= user_id)
        print("-------->{}".format(user_id))
        # add bbox on image
        final_image = add_bboxs_on_img(image = input_image, predict = predict)
        # image = cv2.cvtColor(np.array(final_image), cv2.COLOR_RGB2BGR)
        image = np.array(final_image)
        # image = image[:,:,::-1]
        name_image = re.findall(pattern_name, filename)

        cv2.imwrite("static/uploads/{}_predict.jpg".format(name_image[0]), image)
        # cv2.imwrite("D:/VIETDONG/Predict_Safety_Contructor_Yolov8/PhanLoai/src/assets/{}_predict.jpg".format(name_image[0]), image)
        cv2.imwrite("./PhanLoai/src/assets/{}_predict.jpg".format(name_image[0]), image)

        filename = "{}_predict.jpg".format(name_image[0])
        
        # return render_template('index.html', filename=filename, dangerous=dangerous)
        return { 'dangerous' : dangerous,
                'filename': filename,
                'id': session.get('user_id')}
    
    # else:
        
    #     flash("Allowed image types are - png, jpg, jpeg")
        
    #     return redirect(request.url)
    

@app.route('/display/<filename>')
async def display_images(filename):
    
    return redirect(url_for("static", filename="uploads/" + filename))


@app.route('/predict', methods=["POST"])
async def predict():
    if request.method == "POST":
        file = request.files['file']
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes))
        thread1 = Thread(target=object_json, args=(image,))
        thread1.start()
        thread1.join()
        result = object_json(image)
        
        return jsonify({"result":result})

@app.route('/camera')
async def camera():
    global cap
    if str(session.get('on_cam')) == "0":
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    session['on_cam'] = "1"
    
    return render_template("camera.html")
            
            
@app.route('/video_feed_camera')
async def video_feed_camera():
    global start_camera
    global cap
    if start_camera == 1:
        start_camera = 0
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    return Response(generate_frames_camera(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/result', methods=["GET"])
async def result():
    global dangerous_str
    dangerous_text = dangerous_str
    return {'danger': dangerous_text}

@app.route('/camera_stop', methods=["GET"])
async def start_or_stop():
    global start_camera
    global cap
    if start_camera == 0:
        start_camera = 1
        cap.release()
        cv2.destroyAllWindows()


@app.route('/video')
async def video():
    if str(session.get('on_cam')) == "1":
        session['on_cam'] = "0"
        cap.release()
    return render_template('video.html')

@app.route('/upload_video', methods=['GET', 'POST'])
async def upload_video():
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    session['filename'] = filename
    if os.path.isdir("static/uploads"):
        
        shutil.rmtree("static/uploads")
        
    os.mkdir("static/uploads")
    
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    # return render_template('predict_video.html', filename=filename)
    return {'filename': filename}
            
            
@app.route('/video_feed_video/<filename>')
async def video_feed_video(filename):
    video = cv2.VideoCapture("static/uploads/" + filename)
    return Response(generate_frames_video(video), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(debug = True)