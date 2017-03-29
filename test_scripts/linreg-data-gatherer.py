'''
Track the data needed to form a linear regression for boiler distance vs top-cY
'''

import cv2
import time
import os
import numpy
try:
	import RPi.GPIO as GPIO
except RuntimeError:
	print("Error importing RPi.GPIO!  Probably need to run as root")

## Dirty hack to import GRIP pipeline from parent directory
import sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import grip
## End dirty hack

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
pipeline = grip.GripPipeline()

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

def output_data(data):
	for item in data:
		print("%f  %d" % item) # Mod-item may work because we'd normally just mod a tuple with the same data

if __name__ == '__main__':
	frame = 0
	list_of_data = []
	while True:
		diff=get_diff(mirror=True)
		# cv2.imshow('my webcam', diff)
		if cv2.waitKey(1) == 27:
			temp_sort_list = []
			file_path =  "/tmp/captured_diff%s.png"% frame
			print("Saving last diff image to ", file_path)
			cv2.imwrite(file_path,diff)
			
			pipeline.process(diff)
			contours = pipeline.filter_contours_output
			for contour in contours:
				x, y, w, h = cv2.boundingRect(contour)
				temp_sort_list.append(y)
			
			top_y = sys.maxsize
			for i in range(len(temp_sort_list)):
				if (temp_sort_list[i] < top_y): # < because top = 0, bottom = 360
					top_y = temp_sort_list[i]
			# Now we have our topmost contour's top y-coordinate
			# Pair that up with a distance and profit
			distance = float(raw_input("Distance of capture: "))
			list_of_data.append((distance, top_y))
			
			frame +=1
			#break  # esc or enter to quit
	
	file_path =  "/tmp/captured_diff%s.png" % frame
	print("Saving last diff image to ", file_path)
	cv2.imwrite(file_path,diff)
	output_data(list_of_data)
	print("Cleaning up!!")
	cv2.destroyAllWindows()
	GPIO.cleanup(led_pin)
