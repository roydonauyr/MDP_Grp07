import json
import os
import socket
import time
from pprint import pprint
#import requests

# For images
#import cv2
# import numpy as np
# import torch
# from PIL import Image

# Socket connection with RPI
host = "192.168.7.7"
port = 12345
buffer = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
print("Socket Connected")