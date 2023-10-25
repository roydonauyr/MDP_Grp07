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
from Others.configuration import API_IP, API_PORT

class RaspberryPi:
    """
    Class that represents the Raspberry Pi.
    """

    def __init__(self):
        """
        Initializes the Raspberry Pi.
        """
        # Initializations
        self.android = Android()
        self.manager = Manager()

        # Events
        self.android_dropped = self.manager.Event()

        # Queues
        self.android_queue = self.manager.Queue()  # Messages to send to Android

        # Create processes
        self.process_android_receive = None
        self.process_android_sender = None

        # Lists
        self.current_location = self.manager.dict() # Current location coordinates

    def start(self):
        """
        Starts the RPi orchestrator
        """
        try:
            ### Start up initialization ###
            self.android.connect() # Connect via bluetooth
            self.android_queue.put(AndroidMessage('general', 'You are connected to the RPi!'))

            # Sending location
            self.current_location['x'] = 12
            self.current_location['y'] = 9
            self.current_location['d'] = "N" # 0 is North
            print(f"Current location: {self.current_location}")
            self.android_queue.put(AndroidMessage('location', {
                "x":  self.current_location['x'],
                "y":  self.current_location['y'],
                "d":  self.current_location['d'],
            }))
    

            # Initializing child processes
            self.process_android_receive = Process(target=self.android_receive)
            self.process_android_sender = Process(target=self.android_sender)

            # Start processes
            self.process_android_receive.start() # Receive from android
            self.process_android_sender.start() # Send out information to be displayed on Android
            print("Child processes started!\n")

            ## Start up Complete ##

            
            self.reconnect_android()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
            """Stops all processes on the RPi and disconnects from Android, STM and PC"""
            self.android.disconnect()
            print("Program Ended\n")
    
    def reconnect_android(self):

        print("Reconnection handler is watching\n")

        while True:
            self.android_dropped.wait() # Wait for bluetooth connection to drop with Android.
            print("Android link is down, initiating reconnect\n")

            # Kill child processes
            print("Killing Child Processes\n")
            self.process_android_sender.kill()
            self.process_android_receive.kill()

            # Wait for the child processes to finish
            self.process_android_sender.join()
            self.process_android_receive.join()
            assert self.process_android_sender.is_alive() is False
            assert self.process_android_receive.is_alive() is False
            print("Child Processes Killed Successfully\n")

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
            self.android_queue.put(AndroidMessage("general", "Link successfully reconnected!"))
            self.android_queue.put(AndroidMessage('mode', 'path'))

            self.android_dropped.clear() # Clear previously set event

    def android_receive(self) -> None:
        while True:
            message_rcv: Optional[str] = None
            try:
                message_rcv = self.android.receive()
            except OSError:
                self.android_dropped.set()
                print("Event set: Bluetooth connection dropped")

            if message_rcv is None:
                continue

            # Loads message received from json string into a dictionary
            message: dict = json.loads(message_rcv)

            print(f"Message received: {message}")
    
    def android_sender(self) -> None:
        """
        [Child process] Responsible for retrieving messages from android_queue and sending them over the Android link. 
        """
        while True:
            # Retrieve message from queue
            try:
                message: AndroidMessage = self.android_queue.get(timeout=0.5)
            except queue.Empty:
                self.stop()
                #continue

            try:
                self.android.send(message)
            except OSError:
                self.android_dropped.set()
                print("Event set: Android dropped")

if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()