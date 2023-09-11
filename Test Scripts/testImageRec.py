from RPI.Communication.pc import PC
from RPI.Others.configuration import API_IP, API_PORT
import requests


# def check_api(self) -> bool:
#         """Check whether image recognition and algorithm API server is up and running

#         Returns:
#             bool: True if running, False if not.
#         """
#         # Check image recognition API
#         url = f"http://{API_IP}:{API_PORT}/status"
#         try:
#             response = requests.get(url, timeout=1)
#             if response.status_code == 200:
#                 print("API is up!\n")
#                 #self.logger.debug("API is up!")
#                 return True
#             return False
#         # If error, then log, and return False
#         except ConnectionError:
#             print("API Connection Error\n")
#             #self.logger.warning("API Connection Error")
#             return False
#         except requests.Timeout:
#             print("API Timeout\n")
#             #self.logger.warning("API Timeout")
#             return False
#         except Exception as e:
#             print("Error in api: %s\n", str(e))
#             #self.logger.warning(f"API Exception: {e}")
#             return False

if __name__ == "__main__":
    test = PC()
    test.connect()
    test.send("Image Rec")
    try:
        results = test.camera_cap()
        print(results)
    except Exception as e:
        print("Error in api: %s\n", str(e))
    test.disconnect()