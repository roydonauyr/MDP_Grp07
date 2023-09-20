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
from typing import Optional

def send(message: str) -> None:
    """Send a message to RPI, utf-8 encoded 

    Args:
        message (str): message to send
    """
    
    try:
        # Encode the message as bytes using UTF-8 encoding
        message_bytes = message.encode('utf-8')
        
        # Send the message
        socket.send(message_bytes)
        print(f"Sent To RPI: {message}")

    except Exception as e:
        print(f"Failed to send message: {str(e)}")

def receive() -> Optional[str]:
    """
    Receive data from the RPI over the socket connection.

    Returns:
        str: The received message as a string.
    """
    try:
        unclean_message = socket.recv(1024)
        #self.logger.debug(tmp)
        message = unclean_message.strip().decode("utf-8")
        print("Message received from RPI: %s", str(message))
        #self.logger.debug(f"Received from PC: {message}")
        return message
    except OSError as e:  # connection broken, try to reconnect
        print("Message failed to be received: %s", str(e))
        #self.logger.error(f"Error receiving message from PC: {e}")
        raise e

def capture(expected):
    reply = {}    
    THRESHOLD = 0.7
    
    print("Capture function")
    
    """Capture the last image from cv2.videocapture()"""
    cap.open("http://192.168.7.7:5000/stream.mjpg")

    while True:
        ret, image = cap.read()

        if not ret:
            print("Error: Server not on.")
            continue
    
        # img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img_gray = cv2.resize(image, (640, 640))

        # recognition
        results = model(img_gray)
        output_frame = results.render()[0]
        cv2.imshow('Object Detection', output_frame)

        class_dict = results.names
        
        # """Filter out predictions with confidence less than 0.7"""
        #Convert each prediction to a list
        res = []
        boxes = results.xywh[0]
        boxes = boxes.tolist()

        #Nothing detected, empty tensor
        if len(boxes) == 0:
            print("Nothing captured") # In future implement here send back to move car forward
            continue
        
        """xywh: x,y coordiaante of the center of the bounding box. w,h width height of the bounding box"""
        for box in boxes:
            # Image above midpoint, and small => False
            # if box[1] > 231 and box[3] < 50:
            #     continue
            # # Filter by confidence level
            # elif box[4] > THRESHOLD:
            #     res.append(box)
            print(box)
            if box[4] > THRESHOLD:
                res.append(box)

        new_res = []
        #Remove the bulleyes
        for i in range(len(res)):
            detected_class = class_dict.get(int(res[i][5]))
            if(detected_class != "41"):
                new_res.append(res[i])

        if len(new_res) > 0:
            # biggest_box, mid = res[0], abs(int(res[0][0] - 308))
            # for box in res:
            #     midpoint = abs(int(box[0] - 308))
            #     if midpoint < mid:
            #         biggest_box, mid = box, midpoint
            #     elif box[2] * box[3] > biggest_box[2] * biggest_box[3]:
            #         biggest_box, mid = box, midpoint
            biggest_box = new_res[0]
            
            for box in new_res:
                if box[2] * box[3] > biggest_box[2] * biggest_box[3]:
                    biggest_box = box
        else:
            #Image detected but low accuracy
            print("Low accuracy image")
            continue
        # Print out the x1, y1, w, h, confidence, and class of predicted object
        x, y, w, h, conf, cls_num = biggest_box
        cls = str(int(cls_num))

        x, y, w, h, conf, cls = int(x), int(y), int(w), int(h), round(conf, 2), class_dict.get(int(cls))
        print("Found: {}, {}, {}, {}, {}, {}".format(x, y, w, h, conf, cls))
        
        # #Send image capture to Bluetooth
        # msg_img = "AN|" + "TARGET," + id + ","+ cls
        # s.send(msg_img.encode())
        # time.sleep(0.5)

    #     """how much is the median_detected off from the median_landscape; l is negative, r is positive"""
        median_landscape = 640 / 2
        median_detected = x
        median_diff = median_detected - median_landscape
        median_diff = int(median_diff)
        print("median_diff: ", median_diff)

        reply = {'x': x, 'y': y, 'w': w, 'h': h, 'conf': conf, 'class': cls, 'median': median_diff,
                    'class_num': cls, "median_diff": median_diff}

        # Initialize
        if cls not in expected:
            # Creating an empty folder to store the images of that obstacle
            if(os.path.exists(f"./detected_images/{str(cls)}") == False):
                os.makedirs(f"./detected_images/{str(cls)}")
            
            expected[cls] = [x, y, w, h, conf, cls, median_diff,
                                f"./detected_images/{str(cls)}/conf{str(conf)}_width{w}_height{h}_diff{median_diff}.png"]
            print("*" * 50)
            print(f"Making new directory for class {cls}")
            pprint(expected)
            print("")
            print("")

        # Save the best images metadata
        # Best image is large in bounding box, and has good confidence score (+-0.05)
        #If new image of same id detected and the width(w) and height(h) and conf is more than the original by 0.02 
        #then replace the original
        elif (w >= expected[cls][2] and h >= expected[cls][3]) and (conf >= expected[cls][4] - 0.02):
            expected[cls] = [x, y, w, h, conf, cls, median_diff,
                                f"./detected_images/{str(cls)}/conf{str(conf)}_width{w}_height{h}_diff{median_diff}.png"]
            print("*" * 50)
            print(f"Getting a better image for {cls}")
            pprint(expected)
            print("")
            print("")

        print("*" * 50)
        print("Saving image")
        # Save all predicted images
        cv2.imwrite(f"./detected_images/{str(cls)}/conf{str(conf)}_width{w}_height{h}_diff{median_diff}.png",
                    results.ims[0])
        
        cap.release()
        cv2.destroyAllWindows()
        return reply["class_num"]

# Socket connection with RPI
host = "192.168.7.7"
port = 12345
buffer = 1024
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))
print("Socket Connected")

expected = {}

while True:
    message: Optional[str] = None
    message = receive()
    if message == None:
        print("Waiting for image capture instruction")
        continue
    
    image_dict = {'11': '1', '12': '2', '13': '3', '14': '4', '15': '5', '16': '6', '17': '7', '18': '8', '19': '9', "20": "A", "21":"B", "22": "C", "23": "D", "24": "E", "25":"F", "26": "G", "27": "H", "28": "S", "29": "T", "30": "U", "31": "V", "32": "W","33": "X", "34": "Y", "35": "Z", "36": "UP", "37" : "DOWN", "38": "RIGHT", "39": "LEFT", "40": "STOP"} 

    # Model path
    #model_weights = Path("C:\\Users\\jarel\\Downloads\\task1_best_noFlip.pt")
    #model_weights = Path("C:\\Roydon\\Github\\MDP_Grp07\\yolov5v3.pt")
    model_weights = Path("C:\\Roydon\\Github\\MDP_Grp07\\final.pt")
    model = torch.hub.load('ultralytics/yolov5:master', 'custom', path=model_weights) # Load the YOLOv5 model

    # Access the webcam feed
    cap = cv2.VideoCapture()  # 0 for the default camera, you can specify a different camera if needed

    returned_result = capture(expected)
    if returned_result != None:
        send("Result is: " + returned_result)
    else:
        print(returned_result)
        print("Nothing captured")
