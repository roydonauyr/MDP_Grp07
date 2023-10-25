import json
import os
import socket
import time
from pprint import pprint
#import requests

# For images
import cv2
import numpy as np
import torch
from PIL import Image
from pathlib import Path

def capture():
    
    print("Capture function")
    time.sleep(2)
    """Capture the last image from cv2.videocapture()"""
    cap.open("http://192.168.7.7:5000/stream.mjpg")

    while True:
        ret, image = cap.read()

        if not ret:
            print("Error: Server not.")
            continue
    
        # img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img_gray = cv2.resize(image, (640, 640))

        # recognition
        results = model(img_gray)
        output_frame = results.render()[0]
        cv2.imshow('Object Detection', output_frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Model path
model_weights = Path("C:\\Roydon\\Github\\MDP_Grp07\\final.pt")
#model = torch.hub.load('ultralytics/ultralytics:master', 'custom', path=model_weights)
model = torch.hub.load('ultralytics/yolov5:master', 'custom', path=model_weights) # Load the YOLOv5 model

# Access the webcam feed
cap = cv2.VideoCapture()  # 0 for the default camera, you can specify a different camera if needed

# Socket connection with RPI
host = "192.168.7.7"
port = 12345
buffer = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
print("Socket Connected")
capture()

