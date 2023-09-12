from RPI.Communication.android import Android, AndroidMessage
from multiprocessing import Process, Manager
from typing import Optional

def reconnect_android():
        """
        Handles the reconnection to Android in the event of a lost connection. 
        If connection establised will wait until disconnected before taking action
        """

        print("Reconnection handler is watching\n")
        #self.logger.info("Reconnection handler is watching...")

        # Clean up old sockets
        android.disconnect()

        # Reconnect
        android.connect()


        print("Android processess successfully restarted")
        #self.logger.info("Android child processes restarted")
        print("Reconnection successful")

if __name__ == "__main__":
    android = Android()
    android.connect()
    while True:
        try:
             android.send({"type": "action", "value": "start test"})
        except OSError as e:
             print("Disconnected")
             reconnect_android()
             android.send({"type": "general", "value": "reconnected"})