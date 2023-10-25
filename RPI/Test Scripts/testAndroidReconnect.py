from Communication.android import Android, AndroidMessage
from multiprocessing import Process, Manager
from typing import Optional
import time
import json

def reconnect_android():
        """
        Handles the reconnection to Android in the event of a lost connection. 
        If connection establised will wait until disconnected before taking action
        """

        print("Reconnection handler is watching\n")
        
        # Clean up old sockets
        android.disconnect()

        # Reconnect
        android.connect()
     

        print("Android processess successfully restarted")
        print("Reconnection successful")

if __name__ == "__main__":
    android = Android()
    android.connect()
    while True:
        message_rcv: Optional[str] = None
        try:
             #android.send(AndroidMessage('action', "TARGET,1,20"))
             android.send(AndroidMessage('action', "ROBOT,12,9,N"))
             print("message sent")
             time.sleep(20)
             break
            
        except OSError as e:
             print("Disconnected")
             reconnect_android()
             android.send(AndroidMessage('general', "Reconnected."))


        
