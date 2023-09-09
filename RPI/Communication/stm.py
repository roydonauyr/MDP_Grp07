from typing import Optional
import serial
from Communication.link import Link
from Others.configuration import SERIAL_PORT, BAUD_RATE

class STM(Link):
    """Class for communicating with STM32 microcontroller over UART serial connection.

    ### RPi to STM32
    RPi sends the following commands to the STM32.

    #### Path mode commands
    High speed forward/backward, with turning radius of `3x1`
    - `FW0x`: Move forward `x` units
    - `BW0x`: Move backward `x` units
    - `FL00`: Move to the forward-left location
    - `FR00`: Move to the forward-right location
    - `BL00`: Move to the backward-left location
    - `BR00`: Move to the backward-right location

    #### Manual mode commands
    - `FW--`: Move forward indefinitely
    - `BW--`: Move backward indefinitely
    - `TL--`: Steer left indefinitely
    - `TR--`: Steer right indefinitely
    - `STOP`: Stop all servos

    ### STM32 to RPi
    After every command received on the STM32, an acknowledgement (string: `ACK`) must be sent back to the RPi.
    This signals to the RPi that the STM32 has completed the command, and is ready for the next command.

    """

    def __init__(self):
        """
        Constructor for STMLink.
        """
        super().__init__()
        self.serial = None

    def connect(self):
        """Connect to STM32 using serial UART connection, given the serial port and the baud rate"""
        self.serial = serial.Serial(SERIAL_PORT, BAUD_RATE)
        print("Connected to STM32")
        #self.logger.info("Connected to STM32")

    def disconnect(self):
        """Disconnect from STM32 by closing the serial link that was opened during connect()"""
        self.serial.close()
        self.serial = None
        #self.logger.info("Disconnected from STM32")
        print("Disconnected from STM32")

    def send(self, message: str) -> None:
        """Send a message to STM32, utf-8 encoded 

        Args:
            message (str): message to send
        """
        self.serial.write(f"{message}".encode("utf-8"))
        print("Sent to STM32: %s", str(message))
        #self.logger.debug(f"Sent to STM32: {message}")

    def receive(self) -> Optional[str]:
        """Receive a message from STM32, utf-8 decoded

        Returns:
            Optional[str]: message received
        """
        message = self.serial.readline().strip().decode("utf-8")
        print("Message received from stm: %s", str(message))
        #self.logger.debug(f"Received from STM32: {message}")
        return message
    
    def stmTest(self):
        self.send("R")
        while True:
            message: str = self.receive()
            if message != None:
                print(message)
                break
