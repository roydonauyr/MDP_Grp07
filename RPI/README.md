# Communication Protocols

## Android - RPI
Messages between the Android app and Raspberry Pi will be in the following format:

{"type": "xxx", "value": "xxx"}

The type field will have the following possible values:

general: general messages
error: error messages, usually in response of an invalid action
location: the current location of the robot (in Path mode)
imageRec: image recognition results
status: status updates of the robot (running or finished)
obstacles: list of obstacles
action: movement-related, like starting the run

