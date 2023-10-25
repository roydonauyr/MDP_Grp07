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
        #print("Message failed to be received: %s", str(e))
        #self.logger.error(f"Error receiving message from PC: {e}")
        raise e

def capture(expected):
    reply = {}    
    THRESHOLD = 0.7
    
    print("Capture function")
    
    """Capture the last image from cv2.videocapture()"""
    cap.open("http://192.168.7.7:5000/stream.mjpg")

    counter = 0
    counter_nothing = 0
    first = 1

    while True:
        ret, image = cap.read()

        if not ret:
            if(first):
                fail = True
                stitch(expected, fail)
                first = 0
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
        low_res = []
        boxes = results.xywh[0] # Access the most confident bounding box
        boxes = boxes.tolist()

        #Nothing detected, empty tensor
        if len(boxes) == 0:
            print("Nothing captured") 
            counter_nothing = counter_nothing + 1
            if (counter_nothing >= 3):
                counter_nothing = 0
                return "0"
            continue
        
        """xywh: x,y coordiaante of the center of the bounding box. w,h width height of the bounding box"""
        for box in boxes:
            if box[4] > THRESHOLD:
                res.append(box)
            else:
                low_res.append(box)

        new_res = []
        new_low_res = []

        if(len(res) > 0):
            #Remove the bulleyes
            for i in range(len(res)):
                detected_class = class_dict.get(int(res[i][5]))
                if(detected_class != "bullseye" and detected_class!="99"):
                    new_res.append(res[i])

        if len(new_res) > 0: # Replace biggest bounding box
            biggest_box = new_res[0]
            
            for box in new_res:
                if box[2] * box[3] > biggest_box[2] * biggest_box[3]:
                    biggest_box = box
        else:
            print("Low accuracy image") #Image detected but low accuracy
            counter = counter + 1
            if (counter >= 4):
                counter = 0
            else:
                low_res = []
                continue

        # For low accuracy images
        if(len(low_res) > 0):
            #Remove the bulleyes
            for i in range(len(low_res)):
                low_detected_class = class_dict.get(int(low_res[i][5]))
                if(low_detected_class != "bullseye" and low_detected_class!="99"):
                    new_low_res.append(low_res[i])
                 
        if len(new_low_res) > 0: # Replace biggest bounding box
            biggest_box = new_low_res[0]
            
            for box in new_low_res:
                if box[2] * box[3] > biggest_box[2] * biggest_box[3]:
                    biggest_box = box
       
        # Print out the x1, y1, w, h, confidence, and class of predicted object
        x, y, w, h, conf, cls_num = biggest_box
        cls = str(int(cls_num))

        x, y, w, h, conf, cls = int(x), int(y), int(w), int(h), round(conf, 2), class_dict.get(int(cls))
        print("Found: {}, {}, {}, {}, {}, {}".format(x, y, w, h, conf, cls))
        
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
            
            if(len(low_res) == 0):
                expected[cls] = [x, y, w, h, conf, cls, median_diff,
                                    f"./detected_images/{str(cls)}/conf{str(conf)}_width{w}_height{h}_diff{median_diff}.png"]
            else:
                new_cls = "low" + cls
                expected[new_cls] = [x, y, w, h, conf, cls, median_diff,
                                    f"./detected_images/{str(cls)}/conf{str(conf)}_width{w}_height{h}_diff{median_diff}_low_res.png"]
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
            if(len(low_res) == 0):
                expected[cls] = [x, y, w, h, conf, cls, median_diff,
                                    f"./detected_images/{str(cls)}/conf{str(conf)}_width{w}_height{h}_diff{median_diff}.png"]
            else:
                new_cls = "low" + cls
                expected[new_cls] = [x, y, w, h, conf, cls, median_diff,
                                    f"./detected_images/{str(cls)}/conf{str(conf)}_width{w}_height{h}_diff{median_diff}_low_res.png"]
            print("*" * 50)
            print(f"Getting a better image for {cls}")
            pprint(expected)
            print("")
            print("")

        print("*" * 50)
        print("Saving image")
        # Save all predicted images
        if (len(low_res) == 0):
            cv2.imwrite(f"./detected_images/{str(cls)}/conf{str(conf)}_width{w}_height{h}_diff{median_diff}.png",
                    results.ims[0])
        else:
            print("saved low res")
            print(f"cls:{cls}")
            cv2.imwrite(f"./detected_images/{str(cls)}/conf{str(conf)}_width{w}_height{h}_diff{median_diff}_low_res.png",
                    results.ims[0])
        
        cap.release()
        cv2.destroyAllWindows()
        return reply["class_num"]

def stitch(expected,fail):
    """Stitched the images together. The directory of each image is found in the argument expected on dictionary value[7]."""
    list_of_images = []
    for key in expected.keys():
        list_of_images.append(expected[key][7])
    print(f"Stitching {len(list_of_images)} images: {list_of_images}")
    widths, heights = zip(*(Image.open(i).size for i in list_of_images))
    total_width = max(widths)*int((len(list_of_images)+1)/2)
    max_height = max(heights)*2
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    y_offset = 0
    counter = 0
    for im in list_of_images:
        im = Image.open(im)
        print(f"X: {x_offset}, Y: {y_offset}")
        new_im.paste(im, (x_offset, y_offset))
        counter += 1
        if counter%2 == 0:
            x_offset += im.size[0]
            y_offset = 0
        else:
            y_offset += im.size[1]

    if (fail):
        new_im.save('./Stitched_Images/final_stitched_safety.png')
    else:
        new_im.save('./Stitched_Images/final_stitched.png')

# Socket connection with RPI
host = "192.168.7.7"
port = 12345
buffer = 1024
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))
print("Socket Connected")
model_weights = Path("C:\\Roydon\\Github\\MDP_Grp07\\final.pt")
model = torch.hub.load('ultralytics/yolov5:master', 'custom', path=model_weights) 

expected = {}
#start_time = time.time()
count_no_msg = 0

while True:
    # current_time = time.time()
    # elapsed = current_time - start_time

    # if(elapsed > 210):
    #     print("3.5 minutes have passed, stitching image")
    #     count_no_msg+=1
    #     stitch(expected)
    #     if (count_no_msg > 2):
    #         print("Car stuck, program ended")
    #         break


    message: Optional[str] = None
    try:
        message = receive()
    except Exception as e:
        #print("Waiting for image capture instruction")
        continue
    
    image_dict = {'11': '1', '12': '2', '13': '3', '14': '4', '15': '5', '16': '6', '17': '7', '18': '8', '19': '9', "20": "A", "21":"B", "22": "C", "23": "D", "24": "E", "25":"F", "26": "G", "27": "H", "28": "S", "29": "T", "30": "U", "31": "V", "32": "W","33": "X", "34": "Y", "35": "Z", "36": "UP", "37" : "DOWN", "38": "RIGHT", "39": "LEFT", "40": "STOP"} 
    count_no_msg = 0

    if(message == "Stitch"):
        fail = False
        stitch(expected, fail)
        print("Program ended!")
        break

    # Model path
    # Load the YOLOv5 model

    # Access the webcam feed
    cap = cv2.VideoCapture()  # 0 for the default camera, you can specify a different camera if needed

    returned_result = capture(expected)
    if returned_result != None:
        # send("Result is: " + returned_result)
        send(returned_result)


    
