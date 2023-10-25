from Communication.pc import PC
from Others.configuration import API_IP, API_PORT
import requests



if __name__ == "__main__":
    test = PC()
    test.connect()
    test.send("Image Rec")
    try:
        results = test.old_camera_cap()
        print(results)
    except Exception as e:
        print("Error in api: %s\n", str(e))
    test.disconnect()