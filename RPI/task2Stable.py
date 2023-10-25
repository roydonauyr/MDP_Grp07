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
        self.stm = STM()
        self.pc = PC()
        self.manager = Manager()

        # Events
        self.android_dropped = self.manager.Event()
        self.unpause = self.manager.Event()

        # Locks
        self.movement_lock = self.manager.Lock()

        # Create processes
        self.process_android_receive = None
        self.process_receive_stm = None
        self.process_start_stream = None

        # Ack count
        self.ack_count = 0
        self.first_result = "temp"
        self.second_result = "temp"

     
    def start(self):
        """
        Starts the RPi orchestrator
        """
        try:
            ### Start up initialization ###
            self.android.connect() # Connect via bluetooth
            message: AndroidMessage = AndroidMessage('general', 'You are connected to the RPi!')
            try:
                self.android.send(message)
            except OSError:
                self.android_dropped.set()
                print("Event set: Android dropped")
            #self.android_queue.put(AndroidMessage('general', 'You are connected to the RPi!'))
            self.stm.connect() # Connect via serial
            self.pc.connect() # Connect via socket, rpi ip address

            self.obsSize = int(self.pc.camera_cap())

            # Initializing child processes
            self.process_android_receive = Process(target=self.android_receive)
            self.process_receive_stm = Process(target=self.receive_stm)
            self.process_start_stream = Process(target=self.pc.camera_stream)

            # Start processes
            self.process_android_receive.start() # Receive from android
            self.process_receive_stm.start() # Receive from STM (ACK)
            self.process_start_stream.start() # Start Camera Streaming for Capture Of Image

            print("Child processes started!\n")

            ## Start up Complete ##

            # Send success messages to Android to let you know ready to start
            message: AndroidMessage = AndroidMessage('general', 'Ready to run!')
            try:
                self.android.send(message)
            except OSError:
                self.android_dropped.set()
                print("Event set: Android dropped")
            self.reconnect_android()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
            """Stops all processes on the RPi and disconnects from Android, STM and PC"""
            self.android.disconnect()
            self.stm.disconnect()
            self.pc.disconnect()
            print("Program Ended\n")

    def reconnect_android(self):
        """
        Handles the reconnection to Android in the event of a lost connection. 
        If connection establised will wait until disconnected before taking action
        """

        print("Reconnection handler is watching\n")
        while True:
            
            self.android_dropped.wait() # Wait for bluetooth connection to drop with Android.
            print("Android link is down, initiating reconnect\n")

            # Kill child processes
            print("Killing Child Processes\n")
            self.process_android_receive.kill()

            # Wait for the child processes to finish
            self.process_android_receive.join()
            assert self.process_android_receive.is_alive() is False
            print("Child Processes Killed Successfully\n")

            # Clean up old sockets
            self.android.disconnect()

            # Reconnect
            self.android.connect()

            # Reinitialise Android processes
            self.process_android_receive = Process(target=self.android_receive)

            # Start previously killed processes
            self.process_android_receive.start()

            print("Android processess successfully restarted")

            message: AndroidMessage = AndroidMessage("general", "Link successfully reconnected!")
            try:
                self.android.send(message)
            except OSError:
                self.android_dropped.set()
                print("Event set: Android dropped")

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


            if message_rcv is None:
                continue

            # Loads message received from json string into a dictionary
            message: dict = json.loads(message_rcv)

            ## Command: Set obstacles ##
            if message['type'] == "action":
                if message['value'] == "start":
                    self.movement_lock.acquire()
                    self.stm.send("t000")
                    # self.first_result = self.cap_and_rec("first_image")
                    # if(self.first_result == "38" ): #right
                    #     self.stm.send("RF000") # Increase ack to 6
                    # elif(self.first_result == "39"): #left
                    #     self.stm.send("LF000")
                    # else: # go left by default
                    #      self.stm.send("LF000")
                    print("Moving forward")
                    message: AndroidMessage = AndroidMessage('general', "Moving forward")
                    try:
                        self.android.send(message)
                    except OSError:
                        self.android_dropped.set()
                        print("Event set: Android dropped")

    
    def receive_stm(self) -> None:
        """
        [Child Process] Receive acknowledgement messages from STM, and release the movement lock to allow next movement
        """
        while True:
            message: str = self.stm.receive()
            
            if message.startswith("ACK"):
                self.ack_count+=1
                try:
                    self.movement_lock.release()
                    print("ACK from STM received, movement lock released")
                except Exception:
                    print("Tried to release a released lock")

                if(self.ack_count == 1):
                    self.movement_lock.acquire()
                    self.first_result = self.cap_and_rec("first_image")
                    if(self.first_result == "38"): #right
                        self.stm.send("k000") # Increase ack to 6
                    elif(self.first_result == "39"): #left
                        self.stm.send("j000")
                    else: # go left by default
                         self.stm.send("j000")

                if (self.ack_count == 2): # Ready to scan second obstacle
                    self.movement_lock.acquire()
                    self.second_result = self.cap_and_rec("second_image")
                    print(f"Second result is: {self.second_result}") 
                    if(self.second_result == "3838"): #right, right
                        self.stm.send("h000") 
                    elif(self.second_result == "3939"): #left, left
                        self.stm.send("n000")
                    elif(self.second_result == "3839"): #right, left
                        self.stm.send("g000")
                    elif(self.second_result == "3938"): #left, right
                        self.stm.send("m000")
                    else: # go left by default
                         self.stm.send("n000")
                    self.pc.send("Stitch")

                if (self.ack_count == 3):
                    #self.pc.send("Stitch")
                    self.ack_count = 0
                    self.unpause.clear()
                    message: AndroidMessage = AndroidMessage("general", "Finished run")
                    try:
                        self.android.send(message)
                    except OSError:
                        self.android_dropped.set()
                        print("Event set: Android dropped")
                    #self.stop()   
            else:
                print(f"Ignore unknown message from STM: {message}")


    
    def cap_and_rec(self, obstacle_num: str) -> None:
        """
        RPi snaps an image.
        The response is then forwarded back to the android
        :param obstacle_num: the current obstacle out of 2 that its scanning for
        """
        # Capture image
        print(f"Turn on video stream for obstacle id: {obstacle_num}")
            
        try:
            self.pc.send("Image Rec Start")
            result = self.pc.camera_cap()
        except Exception as e:
            print("Error in sending/receiving message: %s\n", str(e))

        print(f"Results: {result}")
        result_str = f"Result for obstacle {obstacle_num} is: {result}" 
        
        message: AndroidMessage = AndroidMessage("general", result_str)

        try:
            self.android.send(message)
        except OSError:
            self.android_dropped.set()
            print("Event set: Android dropped")

        return result
    

if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()