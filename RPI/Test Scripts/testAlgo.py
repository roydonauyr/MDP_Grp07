import requests
import json
from Others.configuration import API_IP, API_PORT

def check_api() -> bool:
        """Check whether image recognition and algorithm API server is up and running

        Returns:
            bool: True if running, False if not.
        """
        # Check image recognition API
        url = f"http://{API_IP}:{API_PORT}/status"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print("API is up!\n")
                #self.logger.debug("API is up!")
                return True
            return False
        # If error, then log, and return False
        except ConnectionError:
            print("API Connection Error\n")
            #self.logger.warning("API Connection Error")
            return False
        except requests.Timeout:
            print("API Timeout\n")
            #self.logger.warning("API Timeout")
            return False
        except Exception as e:
            print("Error in api: %s\n", str(e))
            #self.logger.warning(f"API Exception: {e}")
            return False
        
def request_algo(data, car_x=1, car_y=1, car_d=0, retrying=False):
        """
        Requests for a series of commands and the path from the Algo API.
        The received commands and path are then placed in their respective queues
        """
        print("Requesting path and commands from algo server.")
        print(f"data: {data}")
        #self.logger.info(f"data: {data}")
        body = {**data, "big_turn": "0", "robot_x": car_x,
                "robot_y": car_y, "robot_dir": car_d, "retrying": retrying}
        url = f"http://{API_IP}:{API_PORT}/path"
        response = requests.post(url, json=body)

        # Error encountered at the server, return early
        if response.status_code != 200:
            print("Something went wrong when requesting path and commands from Algo API.")
            #self.logger.error("Something went wrong when requesting path from Algo API.")
            return

        # Parse response
        result = json.loads(response.content)['data']
        commands = result['commands']
        path = result['path']

        # Print commands received
        print(f"Commands received from API: {commands}")
        #self.logger.debug(f"Commands received from API: {commands}")

        print("\nPrinting commands: \n")
        for c in commands:
            print(c)

        print("\nPrinting path: \n")
        for p in path[1:]:  # ignore first element as it is the starting position of the robot
            print(p)

        print("Commands and path received Algo API. Robot is ready to move.")

if __name__ == "__main__":      
    while True:
        if check_api():
            request_algo({
                "obstacles": [{"x": 5, "y": 10, "id": 1, "d": 2}],
                "mode": "0"
            })