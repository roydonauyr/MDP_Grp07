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
        self.stm = STM()
        self.manager = Manager()

        # Locks
        self.movement_lock = self.manager.Lock()

        self.unpause = self.manager.Event()

        # Queues
        self.command_queue = self.manager.Queue() # Commands from algorithm to be processed by STM
        #self.command_queue.put("SF060")
        self.command_queue.put("P")
        #self.command_queue.put("LF090")
        # self.command_queue.put("SB030")
        # self.command_queue.put("LB090")
        # self.command_queue.put("RB090")
    
        # self.command_queue.put("RF090")
        # self.command_queue.put("RB090")
        # self.command_queue.put("SF010")
        # self.command_queue.put("LF090")
        # self.command_queue.put("SB010")
        # self.command_queue.put("LB090")
        # self.command_queue.put("JF090")
        # self.command_queue.put("JB090")
        # self.command_queue.put("SB010")
        # self.command_queue.put("KF090")
        # self.command_queue.put("KB090")
        # self.command_queue.put("SB010")


        # Create processes
        self.process_receive_stm = None
        self.process_command_execute = None
        self.ack_flag = False

     
    def start(self):
        """
        Starts the RPi orchestrator
        """
        try:
            ### Start up initialization ###
            self.stm.connect() # Connect via serial

            # Initializing child processes
            self.process_receive_stm = Process(target=self.receive_stm)
            self.process_command_execute = Process(target=self.command_execute)

            # Start processes
            self.process_receive_stm.start() # Receive from STM (ACK)
            self.process_command_execute.start() # Commands to Send Out To STM
            print("Child processes started!\n")

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
            """Stops all processes on the RPi and disconnects from Android, STM and PC"""
            self.stm.disconnect()
            print("Program Ended\n")


    def receive_stm(self) -> None:
        while True:
            message: str = self.stm.receive()

            if message.startswith("ACK"):
                try:
                    self.movement_lock.release()

                    print("ACK from STM received, movement lock released")

                except Exception:
                    print("Tried to release a released lock")
            else:
                print(f"Ignore unknown message from STM: {message}")

    def command_execute(self) -> None:
        """
        [Child Process] 
        """
        while True:
            # Retrieve next movement command
            if self.command_queue.empty():
                self.stop()
                break
            command: str = self.command_queue.get()
            print("Wait for unpause")

            self.movement_lock.acquire() # Acquire lock first (needed for both moving, and capturing pictures)

            # STM32 Commands - Send straight to STM32
            stm_prefix = ("SF", "SB", "RF", "RB", "LF", "LB", "JF", "JB", "KF", "KB")
            #stm_prefix = ("FW", "FR", "FL",  "BW", "BR", "BL")

            #if command.startswith(stm_prefix):
                #time.sleep(1)
            self.stm.send(command)
            print(f"Sending to stm: {command}")
            # else:
            #     raise Exception(f"Unknown command: {command}")
            
if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()
    rpi.unpause.wait()