'''
Simply display the contents of the webcam with optional mirroring using OpenCV 
via the new Pythonic cv2 interface.  Press <esc> to quit.
'''

import cv2
import time
import os
import numpy
try:
	import RPi.GPIO as GPIO
except RuntimeError:
	print("Error importing RPi.GPIO!  Probably need to run as root")

led_pin=40
led_high = True
GPIO.setmode(GPIO.BOARD)# Configure the pin counting system to board-style
                        # In this mode it's the pin of the IDC cable
#GPIO.setmode(GPIO.BCM) # Configure the pin counting to internal IO number
GPIO.setup(led_pin,GPIO.OUT)# Configure the GPIO as an output
GPIO.output(led_pin, True)

#NOTE: It's probably unwise to toggle GPIO immediately
# before the image capture. The GPIO may have a turn on time, 
# resulting in incorrect data unless we provide a few
# milliseconds to allow the IO to do it's thing. 
# The best approach is to set the pin mode for the next capture
# immediately after the first one

# Set up the camera properties to avoid stupid problems
os.system("v4l2-ctl -c backlight_compensation=0")
# Your tweaks here
# os.system("v4l2-ctl -c ")

cam = cv2.VideoCapture(0)

def get_diff(mirror=False):
	lightson_ret, lightson_img = cam.read()
	GPIO.output(led_pin, False)
        
	lightsoff_ret, lightsoff_img = cam.read()
	GPIO.output(led_pin, True)

	if not lightson_ret or not lightsoff_ret: 
		print("Invalid image!")
		# This should probably just return a black image 
		# of an appropriate size 
		# (or a really small image that just process as nothing instantly)
		# Alternatively, we can return a tuple with (validity,image)
		height=1
		width=1
		return numpy.zeros((height,width,3), numpy.uint8)

	diff_img = cv2.subtract(lightson_img,lightsoff_img)
	
	if mirror: 
		diff_img = cv2.flip(diff_img, 1)

	return diff_img

if __name__ == '__main__':
	frame = 0
	while True:
		diff=get_diff(mirror=True)
		cv2.imshow('my webcam', diff)
		if cv2.waitKey(1) == 27: 
			file_path =  "/tmp/captured_diff%s.png"% frame
			print("Saving last diff image to ", file_path)
			cv2.imwrite(file_path,diff)
			frame +=1
			#break  # esc or enter to quit
	
	file_path =  "/tmp/captured_diff.png"
	print("Saving last diff image to ", file_path)
	cv2.imwrite(file_path,diff)
	print("Cleaning up!!")
	cv2.destroyAllWindows()
	GPIO.cleanup(led_pin)
