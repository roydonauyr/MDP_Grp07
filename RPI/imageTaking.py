from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.start_preview()
sleep(5)
for i in range(60):
    camera.capture('/home/pi/Desktop/S_middle_%s.jpg' % i)
    print(f"Image taken for {i}")
    sleep(5)
camera.stop_preview()