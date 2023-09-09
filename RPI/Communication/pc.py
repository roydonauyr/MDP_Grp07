import socket
import sys
import time

class PC():
    def __init__(self):
        """
        Initialize the PC connection.
        """
        super().__init__()
        self.host = "192.168.7.7"
        self.port = 12345
        self.connected = False
        self.server_socket = None
        self.client_socket = None

    def connect(self):
        """
        Connect to the PC through socket binding
        """

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Socket established successfully.")

        try:
            self.server_socket.bind((self.host, self.port))
            print("Socket binded successfully.")
        except socket.error as e:
            print("Socket binding failed: %s", str(e))
            self.server_socket.close()
            sys.exit()

        # Wait and accept PC connection
        print("Waiting for PC connection....")
        self.server_socket.listen(128)
        self.client_socket, client_address = self.server_socket.accept()
        print("PC connected successfully from client address of %s", str(client_address))
        self.connected = True


    def disconnect(self):
        try:
            self.server_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.shutdown(socket.SHUT_RDWR)
            self.server_socket.close()
            self.client_socket.close()
            self.server_socket = None
            self.client_socket = None
            self.connected = False
            print("Disconnected from PC successfully.")
        except Exception as e:
            print("Failed to disconnect from PC: %s", str(e))