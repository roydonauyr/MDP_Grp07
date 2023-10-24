import json
import queue
import time
from multiprocessing import Process, Manager
from typing import Optional
import os
from Communication.android import Android, AndroidMessage
from Communication.stm import STM
#from logger import prepare_logger

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

        self.manager = Manager()

        # Events
        self.android_dropped = self.manager.Event()
        self.unpause = self.manager.Event()

        # Locks
        self.movement_lock = self.manager.Lock()

        # Queues
        self.android_queue = self.manager.Queue()  # Messages to send to Android
        self.command_queue = self.manager.Queue() # Commands from algorithm to be processed by STM

        # Create processes
        self.process_android_receive = None
        self.process_receive_stm = None
        self.process_android_sender = None
        self.process_command_execute = None
        self.ack_flag = False
        self.first = True

    def start(self):
        """
        Starts the RPi orchestrator
        """
        try:
            ### Start up initialization ###
            self.android.connect() # Connect via bluetooth
            self.android_queue.put(AndroidMessage('general', 'You are connected to the RPi!'))
            self.stm.connect() # Connect via serial

            # Initializing child processes
            self.process_android_receive = Process(target=self.android_receive)
            self.process_receive_stm = Process(target=self.receive_stm)
            self.process_android_sender = Process(target=self.android_sender)

            # Start processes
            self.process_android_receive.start() # Receive from android
            self.process_receive_stm.start() # Receive from STM (ACK)
            self.process_android_sender.start() # Send out information to be displayed on Android

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
    
    def android_sender(self) -> None:
        """
        [Child process] Responsible for retrieving messages from android_queue and sending them over the Android link. 
        """
        while True:
            # Retrieve message from queue
            try:
                message: AndroidMessage = self.android_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                self.android.send(message)
            except OSError:
                self.android_dropped.set()
                print("Event set: Android dropped")
                #self.logger.debug("Event set: Android dropped")

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
            
            if message['type'] == "start":
                print("Gyro Reset")
                self.stm.send("RS00")
            elif message['type'] == "command":
                if(message['value'] == "up"):
                    self.movement_lock.acquire()
                    self.android_queue.put(AndroidMessage("general", "Moving Forward"))
                    self.stm.send("SF030")
                elif(message['value'] == "down"):
                    self.movement_lock.acquire()
                    self.android_queue.put(AndroidMessage("general", "Moving Backward"))
                    self.stm.send("SB030")
                elif(message['value'] == "left"):
                    self.movement_lock.acquire()
                    self.android_queue.put(AndroidMessage("general", "Moving Left"))
                    self.stm.send("RF090")
                elif(message['value'] == "right"):
                    self.movement_lock.acquire()
                    self.android_queue.put(AndroidMessage("general", "Moving Right"))
                    self.stm.send("LF090")

    def receive_stm(self) -> None:
        """
        [Child Process] Receive acknowledgement messages from STM, and release the movement lock to allow next movement
        """
        while True:

            message: str = self.stm.receive()
            print(message)
            if message.startswith("ACK"):
                # if self.ack_flag == False:
                #     self.ack_flag = True
                #     print("ACK for reset command for STM received")
                #     #self.logger.debug("ACK for RS00 from STM32 received.")
                #     continue
                try:
                    self.movement_lock.release()
                    print("ACK from STM received, movement lock released")


                    # cur_location = self.path_queue.get_nowait()

                    # self.current_location['x'] = cur_location['x']
                    # self.current_location['y'] = cur_location['y']
                    # self.current_location['d'] = cur_location['d']
                    # print(f"Current location: {self.current_location}")
                    #self.logger.info(f"self.current_location = {self.current_location}")
                    # self.android_queue.put(AndroidMessage('location', {
                    #     "x": cur_location['x'],
                    #     "y": cur_location['y'],
                    #     "d": cur_location['d'],
                    # }))

                except Exception:
                    print("Tried to release a released lock")
            else:
                print(f"Ignore unknown message from STM: {message}")
                #self.logger.warning(f"Ignored unknown message from STM: {message}")


if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()