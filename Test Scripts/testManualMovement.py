import json
import queue
import time
from multiprocessing import Process, Manager
from typing import Optional
import os
from RPI.Communication.android import Android, AndroidMessage
from RPI.Communication.stm import STM
#from logger import prepare_logger