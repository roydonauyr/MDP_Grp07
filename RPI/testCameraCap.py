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
        self.pc = PC()
        self.manager = Manager()
        self.streamOn = False

        # Event set
        self.unpause = self.manager.Event()

        # Create processes
        self.process_start_stream = None

         # Locks
        self.movement_lock = self.manager.Lock()

        # Queues
        self.command_queue = self.manager.Queue()
        self.command_queue.put("CAP")
        self.command_queue.put("CAP")
        # self.command_queue.put("CAP")
        # self.command_queue.put("CAP")
        # self.command_queue.put("CAP")
        # self.command_queue.put("CAP")
        # self.command_queue.put("CAP")
        #self.command_queue.put("CAP")
        self.command_queue.put("FIN")

        # Lists
        self.success_obstacles = self.manager.list()

     
    def start(self):
        """
        Starts the RPi orchestrator
        """
        try:
            ### Start up initialization ###
            self.pc.connect() # Connect via socket, rpi ip address

            # Initializing child processes
            self.process_start_stream = Process(target=self.pc.camera_stream)
            self.process_command_execute = Process(target=self.command_execute)

            # Start processes
            self.process_start_stream.start()
            self.process_command_execute.start()

            print("Child processes started!\n")

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
            """Stops all processes on the RPi and disconnects from Android, STM and PC"""
            self.pc.disconnect()
            print("Program Ended\n")


    def command_execute(self) -> None:
        """
        [Child Process] 
        """
        while True:
            # Retrieve next movement command
            print("Sleep Process First")
            time.sleep(10)
            print("Capturing")
            command: str = self.command_queue.get()
            
            print("Wait for movelock")
            self.movement_lock.acquire() # Acquire lock first (needed for both moving, and capturing pictures)

            if command.startswith("CAP"):
                self.pc.send("Image Rec Start")
                message = self.pc.camera_cap()
                print(message)
                self.movement_lock.release()
            elif command.startswith("FIN"):
                self.pc.send("Stitch")
                self.stop() 
            else:
                print("Error in commands")
                raise Exception(f"Unknown command: {command}")
            

if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()
    rpi.unpause.wait()