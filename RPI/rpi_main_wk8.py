import json
import queue
import time
from multiprocessing import Process, Manager
from typing import Optional
import os
import requests
from Communication.android import Android, AndroidMessage
from Communication.stm import STM
from Others.const import SYMBOL_MAPPING
#from logger import prepare_logger
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
        #self.logger = prepare_logger()
        self.android = Android()
        self.stm = STM()

        #self.manager = Manager()


        # Events
        #self.android_dropped = self.manager.Event()
        # self.unpause = self.manager.Event()


        # Locks
        #self.movement_lock = self.manager.Lock()

        # Queues
        #self.android_queue = self.manager.Queue()  # Messages to send to Android
        # Messages that need to be processed by RPi
        #self.rpi_action_queue = self.manager.Queue()
        # Messages that need to be processed by STM32, as well as snap commands
        #self.command_queue = self.manager.Queue()
        # X,Y,D coordinates of the robot after execution of a command
        #self.path_queue = self.manager.Queue()

        #self.process_receive_android = None
        #self.process_receive_stm = None
        #self.process_android_sender = None
        #self.process_command_execute = None
        #self.process_rpi_action = None
        #self.rs_flag = False

        # Lists
        #self.success_obstacles = self.manager.list()
        #self.failed_obstacles = self.manager.list()
        #self.obstacles = self.manager.dict()
        #self.current_location = self.manager.dict()
        #self.failed_attempt = False

    def start(self):
        """
        Starts the RPi orchestrator
        """
    try:
        ### Start up initialization ###
        self.android.connect()
        self.android.repeatMessageTest()

        # self.android_queue.put(AndroidMessage(
        #     'info', 'You are connected to the RPi!'))
        self.stm.connect()
        #self.check_api()

        # # Define child processes
        # self.process_receive_android = Process(target=self.receive_android)
        # self.process_receive_stm = Process(target=self.receive_stm)
        # self.process_android_sender = Process(target=self.android_sender)
        # self.process_command_execute = Process(target=self.command_execute)
        # self.process_rpi_action = Process(target=self.rpi_action)

        # # Start child processes
        # self.process_receive_android.start()
        # self.process_receive_stm32.start()
        # self.process_android_sender.start()
        # self.process_command_execute.start()
        # self.process_rpi_action.start()

        # self.logger.info("Child Processes started")

        # ### Start up complete ###

        # # Send success message to Android
        # self.android_queue.put(AndroidMessage('info', 'Robot is ready!'))
        # self.android_queue.put(AndroidMessage('mode', 'path'))
        # self.reconnect_android()

    except KeyboardInterrupt:
        self.stop()

    # def stop(self):
    #     """Stops all processes on the RPi and disconnects gracefully with Android and STM32"""
    #     self.android.disconnect()
    #     self.stm.disconnect()
    #     self.logger.info("Program exited!")

    # def reconnect_android(self):
    #     """
    #     Handles the reconnection to Android in the event of a lost connection. 
    #     If connection establised will wait until disconnected before taking action
    #     """

    #     self.logger.info("Reconnection handler is watching...")

    #     while True:
    #         # Wait for android connection to drop
    #         self.android_dropped.wait()

    #         self.logger.error("Android link is down!")

    #         # Kill child processes
    #         self.logger.debug("Killing android child processes")
    #         self.process_android_sender.kill()
    #         self.process_receive_android.kill()

    #         # Wait for the child processes to finish
    #         self.process_android_sender.join()
    #         self.process_receive_android.join()
    #         assert self.process_android_sender.is_alive() is False
    #         assert self.process_receive_android.is_alive() is False
    #         self.logger.debug("Android child processes killed")

    #         # Clean up old sockets
    #         self.android.disconnect()

    #         # Reconnect
    #         self.android.connect()

    #         # Recreate Android processes
    #         self.process_android_sender = Process(target=self.android_sender)
    #         self.process_receive_android = Process(target=self.receive_android)

    #         # Start previously killed processes
    #         self.process_android_sender.start()
    #         self.process_receive_android.start()

    #         self.logger.info("Android child processes restarted")
    #         self.android_queue.put(AndroidMessage(
    #             "info", "You are reconnected!"))
    #         self.android_queue.put(AndroidMessage('mode', 'path'))

    #         self.android_dropped.clear()

    
