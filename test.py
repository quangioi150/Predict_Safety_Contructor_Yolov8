import requests
import json
import base64
import imghdr
from PIL import Image
import io
resp = requests.post("http://localhost:5000/predict",
                             files={"file": open('./static/uploads/pm1.jpg', 'rb')})
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

print(objects_detect)
print(dangerous)