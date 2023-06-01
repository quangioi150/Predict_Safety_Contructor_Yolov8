from PIL import Image
import io
import os 
import pandas as pd
import numpy as np
import cv2
import datetime
from threading import Thread
from data.db import *

from typing import Optional
import json 

from ultralytics import YOLO
from ultralytics.yolo.utils.plotting import Annotator, colors

# Initialize the models
model_sample_model = YOLO("./models/best.pt")

today = datetime.date.today().strftime("%d-%m-%Y")


def transform_predict_to_df(results: list, labeles_dict: dict) -> pd.DataFrame:
    """
    Transform predict from yolov8 (torch.Tensor) to pandas DataFrame.

    Args:
        results (list): A list containing the predict output from yolov8 in the form of a torch.Tensor.
        labeles_dict (dict): A dictionary containing the labels names, where the keys are the class ids and the values are the label names.
        
    Returns:
        predict_bbox (pd.DataFrame): A DataFrame containing the bounding box coordinates, confidence scores and class labels.
    """
    # Transform the Tensor to numpy array
    predict_bbox = pd.DataFrame(results[0].to("cpu").numpy().boxes.xyxy, columns=['xmin', 'ymin', 'xmax','ymax'])
    # Add the confidence of the prediction to the DataFrame
    predict_bbox['confidence'] = results[0].to("cpu").numpy().boxes.conf
    # Add the class of the prediction to the DataFrame
    predict_bbox['class'] = (results[0].to("cpu").numpy().boxes.cls).astype(int)
    # Replace the class number with the class name from the labeles_dict
    predict_bbox['name'] = predict_bbox["class"].replace(labeles_dict)
    
    return predict_bbox

def get_model_predict(model: YOLO, input_image: Image, save: bool = False, image_size: int = 1248, conf: float = 0.5, augment: bool = False) -> pd.DataFrame:
    """
    Get the predictions of a model on an input image.
    
    Args:
        model (YOLO): The trained YOLO model.
        input_image (Image): The image on which the model will make predictions.
        save (bool, optional): Whether to save the image with the predictions. Defaults to False.
        image_size (int, optional): The size of the image the model will receive. Defaults to 1248.
        conf (float, optional): The confidence threshold for the predictions. Defaults to 0.5.
        augment (bool, optional): Whether to apply data augmentation on the input image. Defaults to False.
    
    Returns:
        pd.DataFrame: A DataFrame containing the predictions.
    """
    # Make predictions
    predictions = model.predict(
                        imgsz=image_size, 
                        source=input_image, 
                        conf=conf,
                        save=save, 
                        augment=augment,
                        flipud= 0.0,
                        fliplr= 0.0,
                        mosaic = 0.0,
                        )
    
    # Transform predictions to pandas dataframe
    predictions = transform_predict_to_df(predictions, model.model.names)
    return predictions


def add_bboxs_on_img(image: Image, predict: pd.DataFrame()) -> Image:
    """
    add a bounding box on the image

    Args:
    image (Image): input image
    predict (pd.DataFrame): predict from model

    Returns:
    Image: image whis bboxs
    """
    # Create an annotator object
    annotator = Annotator(np.array(image))

    # sort predict by xmin value
    predict = predict.sort_values(by=['xmin'], ascending=True)

    # iterate over the rows of predict dataframe
    for i, row in predict.iterrows():
        # create the text to be displayed on image
        text = f"{row['name']}: {int(row['confidence']*100)}%"
        # get the bounding box coordinates
        bbox = [row['xmin'], row['ymin'], row['xmax'], row['ymax']]
        # add the bounding box and text on the image
        annotator.box_label(bbox, text, color=colors(row['class'], True))
    # convert the annotated image to PIL image
    return Image.fromarray(annotator.result())


def detect_sample_model(input_image: Image) -> pd.DataFrame:
    """
    Predict from sample_model.
    Base on YoloV8

    Args:
        input_image (Image): The input image.

    Returns:
        pd.DataFrame: DataFrame containing the object location.
    """
    predict = get_model_predict(
        model=model_sample_model,
        input_image=input_image,
        save=False,
        image_size=640,
        augment=False,
        conf=0.5,
    )
    return predict


def crop_image_by_predict(image: Image, predict: pd.DataFrame(), crop_class_name: str,) -> Image:
    """Crop an image based on the detection of a certain object in the image.
    
    Args:
        image: Image to be cropped.
        predict (pd.DataFrame): Dataframe containing the prediction results of object detection model.
        crop_class_name (str, optional): The name of the object class to crop the image by. if not provided, function returns the first object found in the image.
    
    Returns:
        Image: Cropped image or None
    """
    crop_predicts = predict[(predict['name'] == crop_class_name)]

    if crop_predicts.empty:
        
        return None

    # if there are several detections, choose the one with more confidence
    if len(crop_predicts) > 1:
        crop_predicts = crop_predicts.sort_values(by=['confidence'], ascending=False)

    crop_bbox = crop_predicts[['xmin', 'ymin', 'xmax','ymax']].iloc[0].values
    # crop
    img_crop = image.crop(crop_bbox)
    return(img_crop)


def save_object(input_image):
    """
    Object Detection from an image.

    Args:
        input_image (bytes): The image file in bytes format.
    Returns:
        image: image or None
    """
    color_coverted = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    
    input_image = Image.fromarray(color_coverted)
    predict = detect_sample_model(input_image)
    print('aaaa',predict)
    
    path = './static/object/'
    today = datetime.date.today().strftime("%Y-%m-%d")
    folder_path = os.path.join(path, today)
    
    os.makedirs(folder_path, exist_ok=True)
    
    # Get the count of existing folders
    existing_folders = sum(
        1 for entry in os.scandir(folder_path)
        if entry.is_dir() and entry.name.startswith("run")
    )

    # Generate a new folder name
    folder_name = f"run{existing_folders + 1}"
    folder_path = os.path.join(folder_path, folder_name)

    # Create a new folder
    os.mkdir(folder_path)
                
    classes = predict['name']
    for cls in classes:
        
        object = crop_image_by_predict(input_image, predict, crop_class_name = cls)
        object.save("{}/{}.jpg".format(folder_path,cls))


def object_json(filename):
    """
    Object Detection from an image.

    Args:
        file (bytes): The image file in bytes format.
    Returns:
        dict: JSON format containing the Objects Detections.
    """
    # Step 1: Initialize the result dictionary with None values
    result={'detect_objects': None}

    # Step 2: Predict from model
    predict = detect_sample_model(filename)

    # Step 3: Select detect obj return info
    # here you can choose what data to send to the result
    detect_res = predict[['name', 'confidence']]
    objects = detect_res['name'].values

    result['detect_objects_names'] = ', '.join(objects)
    result['detect_objects'] = json.loads(detect_res.to_json(orient='records'))

    return result

def get_prediction(input_image):
    
    predict = detect_sample_model(input_image)
    
    result = object_json(input_image)
    dangerous = []
    
    objects_detect = result["detect_objects_names"].replace(" ", "").split(',')
    if 'NO-SafetyVest' in objects_detect:
        dangerous.append('NO-Safety Vest')
    if 'NO-Hardhat' in objects_detect:
        dangerous.append('NO-Hardhat')
    if "NO-Mask" in objects_detect:
        dangerous.append("NO-Mask")
    # add bbox on image
    final_image = add_bboxs_on_img(image = input_image, predict = predict)
    
    image = cv2.cvtColor(np.array(final_image), cv2.COLOR_RGB2BGR)
    
    image = cv2.resize(image[:,:,::-1], (640, 480))
    
    return image, dangerous


def create_folder(path):
    
    today = datetime.date.today().strftime("%d-%m-%Y")
    folder_path = os.path.join(path, today)
    
    os.makedirs(folder_path, exist_ok=True)
    
    # Get the count of existing folders
    existing_folders = sum(
        1 for entry in os.scandir(folder_path)
        if entry.is_dir() and entry.name.startswith("run")
    )

    # Generate a new folder name
    folder_name = f"run{existing_folders + 1}"
    folder_path = folder_path + "/" + folder_name

    # Create a new folder
    os.mkdir(folder_path)
    
    return folder_path


def get_parameters(conn, image, user_id):
    
    image_predict, dangerous = get_prediction(image)
    if len(dangerous) == 0:
        predictions = 'SAFETY'
    else:
        predictions = 'Dangerous'

    folder_path = create_folder(path = './PhanLoai/src/assets/')
    result = object_json(image)
    
    path_image = folder_path + "/predict.jpg"
    cv2.imwrite(path_image, image_predict)
    Images = path_image
    
    insert_images(conn, user_id, Images, predictions)
    print(user_id)
    print(Images)
    print(predictions)
    NgayTest = today
    image_id = get_image_id_current(conn)
    print('-----',image_id)
    for obj in result['detect_objects']:
        
        name = obj["name"]
        confidence = obj["confidence"]
        
        insert_results(conn, image_id, name, NgayTest, confidence)
        print('------name',name)
        # print(image_id, name, confidence)
        
        
from collections import defaultdict

def get_average(results):
    averages = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for item in results:
        image_id = item["ImageID"]
        name_object = item["NameObject"]
        do_chinh_xac = item["DoChinhXac"]
        image = item["Images"]

        averages[image_id][name_object][image].append(do_chinh_xac)

    # Tính trung bình cộng và gộp kết quả
    result = []
    for image_id, name_objects in averages.items():
        for name_object, images in name_objects.items():
            for image, do_chinh_xacs in images.items():
                average = sum(do_chinh_xacs) / len(do_chinh_xacs)
                result.append({
                    "UserID": results[0]["UserID"],
                    "Images": image,
                    "ImageID": image_id,
                    "NameObject": name_object,
                    "NgayTest": results[0]["NgayTest"],
                    "DoChinhXac": average
                })

    return result