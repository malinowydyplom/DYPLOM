
from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.resolution = (720, 400)
camera.framerate = 32



camera.start_preview()
camera.start_recording('/home/pi/video.h264')
sleep(15)
camera.stop_recording()
camera.stop_preview()
