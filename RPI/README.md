# Communication Protocols

## Android - RPI
Messages between the Android app and Raspberry Pi will be in the following format:

{"type": "xxx", "value": "xxx"}

The type field will have the following possible values:

general: general messages
mode: path (0) or manual (1)
error: error messages, usually in response of an invalid action
status: status updates of the robot (running or finished)
obstacles: list of obstacles
action: movement-related, like starting the run
imageRec: image recognition results
location: the current location of the robot (in Path mode)


### General Messages
Examples of messages (Msg | Explanation)
* You are connected to the RPi! | Android successfully connected to RPI
* Ready to run! | All child processes have started
* Link successfully reconnected! | In the event of the connection dropping, this message appears after successfully reconnecting
* Starting robot on path! | Android tablet sending the start command to RPI
* Requesting path and commands from algo server... | Retreiving path and commands from algo
* Commands queue finished! | RPI finished executing all commands in queue
* Capturing image for obstacle id: {pbstacle_id} | RPI capturing an image on camera for an obstacle
* Commands and path received Algo API. Robot is ready to move. | Upon receiving commands from algo server
* Images stitched! | Successful stitching of the images

### Error Messages
Examples of messages (Msg | Explanation)
API is down, start command aborted | When algo api is not ready
Command queue is empty, did you set obstacles? | When there are no commands in queue
Something went wrong when requesting stitch from the API. | When stitching fails from api
Something went wrong when requesting path and commands from Algo API. | When failing to request path from algo
Something went wrong when requesting result from Image Rec API. | When failing to get the prediction from image rec

### Status Messages
Examples of messages (Msg | Explanation)
* running | When the robot is running
* finished | When the robot has finished running

### Obstacle Format
Message format when sending from Android to RPI
Obstacle should contain: Coordinates, id, direction of obstacle to scan from
{
"type": "obstacles",
"value": {
    "obstacles": [{"x": 5, "y": 10, "id": 1, "d": 2}],
    "mode": "0"
}
}

### Start Movement
Message format when sending from Android to RPI to start robot movement (follow command queue)
{"type": "action", "value": "start"}

If there are no commands in the queue, RPI will respond with an error to Android
{"type": "error", "value": "Command queue is empty, did you set obstacles?"}

### Image Recognition
Message format when sending from RPI to Android after predictions have been received so that Android can update the results of the image recognition
{"type": "imageRec", "value": {"image_id": "21", "obstacle_id":  "1"}}

### Location Updates
Message format when sending from RPI to Android to update the location of the robot periodically
Value includes: Coordinates, Direction of robot
{"type": "location", "value": {"x": 1, "y": 1, "d": 0}}

## STM Commands
Below are the possible commands that are used for the robot's movement. Commands come from algo/RPI to be executed by stm (pass from RPI to stm) or could also be for PC to execute (Such as CAP/FIN)

### Task 1 Commands:
Commands | Explanation
#### STM Commands
* RSOO | Resetting the gyro before starting movement
* SFxx | Move robot forward by xx units
* RF00 | Move robot forward and right by 3x2 squares
* LF00 | Move robot forward left by 3x2 squares
* SBxx | Robot moves backward by xx units
* RB00 | Robot moves backward right by 3x2 squares
* LB00 | Robot moves backward left by 3x2 squares


#### Misc Commands
* STOP | Robot stops moving
* CAP | Robot takes a picture from video stream and send for inference
* FIN | Robot stops moving, stitches images and send a message to the server to signal end of command queue

#### Acknowledgement from STM to remove movement lock
* ACK | Acknowledgement after receiving and executing a command


# TO RUN BLUETOOTH:
To work on virtual env:
workon testing
cd dir RPI

Through script: sudo /home/pi/.virtualenvs/testing/bin/python rpi_main_wk8.py

For testing:
echo "Hi from RPI" > /dev/rfcomm0
to listen: cat /dev/rfcomm0
