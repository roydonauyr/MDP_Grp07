import json
import queue
import time
from multiprocessing import Process, Manager
from typing import Optional
import os
#import requests

from Communication.android import Android, AndroidMessage 
from Communication.stm import STM
from Others.configuration import API_IP, API_PORT

class RPiAction:
    """
    Class that represents an action that the RPi needs to take.    
    """

    def __init__(self, type, value):
        """
        :param cat: The category of the action. Can be 'info', 'mode', 'path', 'snap', 'obstacle', 'location', 'failed', 'success'
        :param value: The value of the action. Can be a string, a list of coordinates, or a list of obstacles.
        """
        self._type = type
        self._value = value

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value
    
class RaspberryPi:
    """
    Class that represents the Raspberry Pi.
    """

    def __init__(self):
        """
        Initializes the Raspberry Pi.
        """
        self.stm = STM()

    def start(self):
        """
        Starts the RPi orchestrator
        """
        try:
            ### Start up initialization ###
            self.stm.connect()
            self.stm.stmTest()
            self.stm.disconnect()
        except KeyboardInterrupt:
            self.stop()


if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()