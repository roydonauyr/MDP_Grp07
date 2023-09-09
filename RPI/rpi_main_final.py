import json
import queue
import time
from multiprocessing import Process, Manager
from typing import Optional
import os
import requests
from Communication.android import Android, AndroidMessage
from Communication.stm import STM
from Communication.pc import PC
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
        # Initializations
        #self.logger = prepare_logger()
        self.android = Android()
        self.stm = STM()
        self.pc = PC()
        self.manager = Manager()

        # Events
        self.android_dropped = self.manager.Event()
        self.unpause = self.manager.Event()

        # Locks
        self.movement_lock = self.manager.Lock()

        # Queues
        self.android_queue = self.manager.Queue()  # Messages to send to Android
        self.rpi_action_queue = self.manager.Queue() # Actions to be performed by RPI
        self.command_queue = self.manager.Queue() # Commands from algorithm to be processed by STM
        self.path_queue = self.manager.Queue() # X,Y,d Coordinates of the robot after execution of the command

        # Create processes
        self.process_android_receive = None
        self.process_receive_stm = None
        self.process_android_sender = None
        self.process_command_execute = None
        self.process_rpi_action = None
        self.ack_flag = False

        # Lists
        self.success_obstacles = self.manager.list()
        self.failed_obstacles = self.manager.list()
        self.obstacles = self.manager.dict() # List ofobstacles
        self.current_location = self.manager.dict() # Current location coordinates
        self.failed_attempt = False

     
    def start(self):
        """
        Starts the RPi orchestrator
        """
        try:
            ### Start up initialization ###
            self.android.connect() # Connect via bluetooth
            self.android_queue.put(AndroidMessage('general', 'You are connected to the RPi!'))
            self.stm.connect() # Connect via serial
            self.pc.connect() # Connect via socket, rpi ip address
            self.check_api() # Checks if api of algo server is running

            # Initializing child processes
            self.process_android_receive = Process(target=self.android_receive)
            self.process_receive_stm = Process(target=self.receive_stm)
            self.process_android_sender = Process(target=self.android_sender)
            self.process_command_execute = Process(target=self.command_execute)
            self.process_rpi_action = Process(target=self.rpi_action)

            # Start processes
            self.process_android_receive.start() # Receive from android
            self.process_receive_stm.start() # Receive from STM (ACK)
            self.process_android_sender.start() # Send out information to be displayed on Android
            self.process_command_execute.start() # Commands to Send Out To STM
            self.process_rpi_action.start() # Different RPI Actions (1. Receive obstacles and send to algo)

            # self.logger.info("Child Processes started")
            print("Child processes started!\n")

            ## Start up Complete ##

            # Send success messages to Android to let you know ready to start
            self.android_queue.put(AndroidMessage('general', 'Ready to run!'))
            self.android_queue.put(AndroidMessage('mode', 'path'))
            self.reconnect_android()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
            """Stops all processes on the RPi and disconnects from Android, STM and PC"""
            self.android.disconnect()
            self.stm.disconnect()
            self.pc.disconnect()
            print("Program Ended\n")
            #self.logger.info("Program exited!")

    def check_api(self) -> bool:
        """Check whether image recognition and algorithm API server is up and running

        Returns:
            bool: True if running, False if not.
        """
        # Check image recognition API
        url = f"http://{API_IP}:{API_PORT}/status"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print("API is up!\n")
                #self.logger.debug("API is up!")
                return True
            return False
        # If error, then log, and return False
        except ConnectionError:
            print("API Connection Error\n")
            #self.logger.warning("API Connection Error")
            return False
        except requests.Timeout:
            print("API Timeout\n")
            #self.logger.warning("API Timeout")
            return False
        except Exception as e:
            print("Error in api: %s\n", str(e))
            #self.logger.warning(f"API Exception: {e}")
            return False
        
    def reconnect_android(self):
        """
        Handles the reconnection to Android in the event of a lost connection. 
        If connection establised will wait until disconnected before taking action
        """

        print("Reconnection handler is watching\n")
        #self.logger.info("Reconnection handler is watching...")

        while True:
            
            self.android_dropped.wait() # Wait for bluetooth connection to drop with Android.
            print("Android link is down, initiating reconnect\n")
            #self.logger.error("Android link is down!")

            # Kill child processes
            print("Killing Child Processes\n")
            #self.logger.debug("Killing android child processes")
            self.process_android_sender.kill()
            self.process_android_receive.kill()

            # Wait for the child processes to finish
            self.process_android_sender.join()
            self.process_android_receive.join()
            assert self.process_android_sender.is_alive() is False
            assert self.process_android_receive.is_alive() is False
            print("Child Processes Killed Successfully\n")
            #self.logger.debug("Android child processes killed")

            # Clean up old sockets
            self.android.disconnect()

            # Reconnect
            self.android.connect()

            # Reinitialise Android processes
            self.process_android_sender = Process(target=self.android_sender)
            self.process_android_receive = Process(target=self.android_receive)

            # Start previously killed processes
            self.process_android_sender.start()
            self.process_android_receive.start()

            print("Android processess successfully restarted")
            #self.logger.info("Android child processes restarted")
            self.android_queue.put(AndroidMessage("general", "Link successfully reconnected!"))
            self.android_queue.put(AndroidMessage('mode', 'path'))

            self.android_dropped.clear() # Clear previously set event

    def android_receive(self) -> None:
        """
        [Child Process] Processes the messages received from Android Tablet
        """
        while True:
            message_rcv: Optional[str] = None
            try:
                message_rcv = self.android.receive()
            except OSError:
                self.android_dropped.set()
                print("Event set: Bluetooth connection dropped")
                #self.logger.debug("Event set: Android connection dropped")

            if message_rcv is None:
                continue

            # Loads message received from json string into a dictionary
            message: dict = json.loads(message_rcv)

            ## Command: Set obstacles ##
            if message['type'] == "obstacles":
                self.rpi_action_queue.put(RPiAction(**message))
                print("Rpi Action To Set Obstacles Added")
                #self.logger.debug(f"Set obstacles PiAction added to queue: {message}")

            ## Command: Start Moving ##
            elif message['type'] == "action":
                if message['value'] == "start":
                    # Check if APIs are up and running
                    if not self.check_api():
                        print("API for Algo is not up")
                        #self.logger.error("API is down! Start command aborted.")
                        self.android_queue.put(AndroidMessage('error', "API is down, start command aborted."))

                    # Commencing path following if command queue has been populated from algo
                    if not self.command_queue.empty():
                        #self.logger.info("Gryo reset!")
                        print("Gyro Reset")
                        self.stm.send("RS00")
                        
                        # Main trigger to start movement #
                        self.unpause.set() # Set event unpause
                        print("Start command received, robot will now move on path")
                        #self.logger.info("Start command received, starting robot on path!")
                        self.android_queue.put(AndroidMessage('general', 'Starting robot on path!'))
                        self.android_queue.put(AndroidMessage('status', 'running'))
                    else:
                        print("Command Queue is empty, please set obstacles")
                        #self.logger.warning("The command queue is empty, please set obstacles.")
                        self.android_queue.put(AndroidMessage("error", "Command queue is empty, did you set obstacles?"))


if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()