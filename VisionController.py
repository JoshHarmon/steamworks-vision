"""
2017 Steamworks vision code for Team 2811 (StormBots)

Picks a boiler-like target and pushes values for the RIO
to do *fun* calculations with.

Coordinate for alignment: vision --> boiler_alignment_cy
Coordinate for distance : vision --> boiler_distance_cx
"""

import cv2
import numpy as np
from grip import GripPipeline

import os
from networktables import NetworkTables
import logging

import time
import sys
import math
import datetime
import traceback

# tested using pip package Adafruit-GPIO
# sudo pip install Adafruit-GPIO
import RPi.GPIO as GPIO

from concurrent.futures import ThreadPoolExecutor

##
## Meaty vision functions!
##
height=480
width=640
blank = np.zeros((height,width,3),np.uint8)

def get_diff_sources():
	#start = time.time()
	#t=[]
	#GPIO.output(led_pin, True)
	#t.append(time.time())
	lightson_ret, lightson_img = cam.read()
	#t.append(time.time())
	GPIO.output(led_pin, False)
	#t.append(time.time())
	lightsoff_ret, lightsoff_img = cam.read()
	#t.append(time.time())
	GPIO.output(led_pin, True)
	#t.append(time.time())
	
	if not lightson_ret or not lightsoff_ret: 
		print("Invalid image!")
		# This should probably just return a black image 
		# of an appropriate size 
		# (or a really small image that just process as nothing instantly)
		# Alternatively, we can return a tuple with (validity,image)
		return (False, blank,blank )

	#t.append(time.time())
	#for i in t:
		#print(i-start)

	return (True, lightson_img,lightsoff_img)

def get_target_xy(img):
	# print("processing... processing... PROCESSING.")

	grip.process(img)
	contours = grip.filter_contours_output

	img2 = cv2.drawContours(img, contours, -1, (0,255,0), 3)

	if drawmode==DRAW_CONTOURS:
		cv2.imshow('diff w/ contours', img2)
		if cv2.waitKey(1) == 27: # Esc
			cv2.destroyAllWindows()
			
	# data array of basic contour properties
	dArr = []

	for i in range(len(contours)):
		moments1 = cv2.moments(contours[i])

		cx = int(moments1['m10']/moments1['m00'])
		cy = int(moments1['m01']/moments1['m00'])

		area = cv2.contourArea(contours[i])

		dArr.append([i, cx, cy, area])
		
	dArr.sort(key=lambda x: x[3], reverse=True)
	
	## Traits: Group Height, dTop, LEdge, Width ratio, Height ratio

	traitAnalysisArr = []
	
	for i in range(len(dArr) - 1): ## range stops before the length, so this stays in bounds
		for j in range(i + 1, len(dArr)):
			## The non-2 values should represent the top target (as we sort dArr by area and the top target is bigger)
			## The -2 values, logically, represent the bottom target rect values
			x,y,w,h = cv2.boundingRect(contours[dArr[i][0]])  ## dArr[i][0] represents the true i-value of the contour
			x2,y2,w2,h2 = cv2.boundingRect(contours[dArr[j][0]])

			## See how well the left edges of the targets line up
			lEdgeTestValue = abs((((x - x2) / w) + 1))

			## As we are are iterating with bigger contours in i, these values should not get inverted
			widthCompareTestValue = abs((w / w2)) ## Widths should be about the same
			heightCompareTestValue = abs((h / (2*h2))) ## Top should be about twice as tall as bottom

			areaCompareValue = abs(((w * h) / (w2 * h2)) - 2) ## .5 or (2) (2 should be forced by iteration order)

			totalTestScore = lEdgeTestValue + widthCompareTestValue + heightCompareTestValue + areaCompareValue

			traitAnalysisArr.append([i, j, totalTestScore])

	bestIdx = 0
	bestScore = sys.maxsize # Remember: the scores are like golf; lower is better. Anything will be lower than maxsize

	if (len(traitAnalysisArr) > 0): # Do we have any contour pairs?
		for i in range(len(traitAnalysisArr)):
			if (traitAnalysisArr[i][2] < bestScore):
				bestIdx = i
				bestScore = traitAnalysisArr[i][2]
				
		print('Best score: pair', traitAnalysisArr[i], 'with a score of', traitAnalysisArr[i][2], '')
		print('   ^ Contour 1: ', dArr[traitAnalysisArr[i][0]], ' || Contour 2: ', dArr[traitAnalysisArr[i][1]])
		
		top_contour_data = dArr[traitAnalysisArr[bestIdx][0]]

		dist_cy = top_contour_data[2]
		dist_cx = top_contour_data[1]
		
		return True,dist_cx,dist_cy
	else:
		return False,0,0

def get_distance_to_boiler(target_cy):

	## TODO: Optimize to use FOV in rad to remove the conversion
	## TODO: Optimize to get cx as either arg or pass in dArr item
	

	# The angle the camera is tilted *back* at. Center pixel represents this angle.
	camera_angle = 38

	# Angle of top pixel, which is added to camera_angle to produce an angle for the
	# top pixel (cy = 0) of the image. Then, after this, we can subtract cy * (vfov/px)
	fov_angle_top = (52.0175 / 2.0) # /2 because we want only the top half of the FOV
	vertical_angle_offset = (target_cy * 1/24.6071)

	total_angle = camera_angle + fov_angle_top - vertical_angle_offset

	'''
	tan(total_angle) = boiler_height / distance
	
	distance * tan(total_angle) = boiler_height
	
	distance = boiler_height / tan(total_angle)
	'''
	# Dan's magic equations
	#angle_from_vertical = cam_deg+(calculated pixel from top)*cam_fov
	angle_from_vertical = camera_angle+target_cy/480*52.0175
	angle_from_horizon = 90-angle_from_vertical
	total_angle = angle_from_horizon
	
	print("CY ",target_cy)
	print("Angle ",total_angle)


	target_height = 8 + (2/12.0)  - (44/12.0)   # approx height of top target (trig: opp) !!!! MINUS THE CAMERA TEST HEIGHT VALUE !!!!
	
	total_angle_rad = total_angle * (math.pi / 180.0)

	distance = target_height / math.tan(total_angle_rad)
	print("Distance ", distance)

	return distance

def distance_from_interpolation_portrait(target_cx):
	table = np.array([
			##[PX, DISTANCE]
				[1,2],
				[3,4],
				[5,6]
			])
	i = 0
	while target_cx > interpolation_table[i][0] and i < len(interpolation_table) - 1:
		i++
	#   Initial point  +    S            L             O             P                E       *     deltaX
	return table[i][1] + ((table[i+1][1] - table[i][1]) / (table[i+1][0] - table[i][0])) * (target_cx - table[i][0])
	
'''
                    UP                                       RIGHT
        LEFT                    RIGHT                UP             DOWN               
                    DOWN                                     LEFT

RIGHT is now y = 0
UP is now x = 0
LEFT is now y = 360
DOWN is now x = 640

'''

def push_coordinate_for_distance_portrait(target_cx):
	if NetworkTables.isConnected():
		try:
			table.putNumber("boiler_distance_cx", target_cx)
			return True
		except:
			return False
	else:
		return False

def push_coordinate_for_alignment_portrait(target_cy):
	if NetworkTables.isConnected():
		try:
			table.putNumber("boiler_angle_cy", target_cy)
			return True
		except:
			return False
	else:
		return False
	
def distance_from_regression(target_cy):
	# From the regression, the math works out to be:
	# px = 50.044 * disFt - 164.316
	# px - 164.316 = 50.044 * disFt
	# (px - 164.316) / 50.044 = disFt
	
	return (px - 164.316) / 50.044

def get_horizontal_angle_offset(target_cx):
	degrees_per_px = 1 / 12.30355
	angle_offset = degrees_per_px * (target_cx - 320)
	return angle_offset

##
## GENERAL SETUP SUB ROUTINES
## 
def set_os_camera_parameters():
	# Set up the camera properties to avoid stupid problems
	os.system("v4l2-ctl -c backlight_compensation=0")
	# Your tweaks here
	# os.system("v4l2-ctl -c ")

def LED_initialize(led):
	led_high = True
	GPIO.setmode(GPIO.BOARD)# Configure the pin counting system to board-style
							# In this mode it's the pin of the IDC cable
	#GPIO.setmode(GPIO.BCM) # Configure the pin counting to internal IO number
	GPIO.setup(led,GPIO.OUT)# Configure the GPIO as an output
	GPIO.output(led, True)

led_pin = 40
table = None
cam = None
frame_count = 0
enabled = False

DEBUG = False

drawmode = 0
DRAW_DISABLED = 0
DRAW_DIFF = 1
DRAW_CONTOURS = 2

grip = GripPipeline()

def noop():
	pass

def image_process_pipeline(img_on,img_off,frame,mirror=True):
	ptime = time.time()

	img = cv2.subtract(img_on, img_off)
	
	if mirror: 
		img = cv2.flip(img, 1)

	
	valid,x_pos,y_pos = get_target_xy(img)
	if not valid:
		return (False,0,0,frame_count)
	
	#distance = get_distance_to_boiler(y_pos)
	#distance = distance_from_regression(y_pos)
	#angle = get_horizontal_angle_offset(x_pos)

	# Do cool stuff with valid data
	if valid:
		# Post data to NWTables
		# update frame_count
		try:
			#table.putNumber("boiler_angle", angle)
			#table.putNumber("boiler_distance", distance)
			#table.putNumber("boiler_frame_count", frame_count)
			push_coordinate_for_alignment_portrait(target_cy)
			push_coordinate_for_distance_portrait(target_cx)
		except KeyError:
			not DEBUG and print("Error: NT not connected @ data post")
		
	if valid and DEBUG:
		print("Successfully processed frame %s" % frame_count)
		print("time:",time.strftime("%a, %d %b %Y %H:%M:%S.%f", time.gmtime()))
		print("Horizontal angle :%02.4f degrees" % angle)
		print("Distance         :%02.4f feet " % distance)
		print("======")
	
	#Uncomment to slow down the reporting stream
	#and/or prove the multithreading works as expected
	#time.sleep(0.4)
		
	ptime = time.time()-ptime
	ptime = "%2.5fs" % ptime
	
	# Returned for convenience in printing
	# Handle usage of this data in this thread
	return (valid, distance, angle,frame,ptime)


process_pool = ThreadPoolExecutor(1)
process_thread = process_pool.submit(noop)

if __name__ == '__main__':
	LED_initialize(led_pin)

	# Check for debug flag
	if "--debug" in sys.argv or "-d" in sys.argv:
			print("Debug mode activated!")
			DEBUG=True
			drawmode=DRAW_CONTOURS
			#drawmode=DRAW_DIFF
			#drawmode=DRAW_DISABLED
			
	while ( NetworkTables.isConnected() == False or table == None):
		# Attempt connection to NetworkTables
		try:
			NetworkTables.initialize(server="roboRIO-2811-FRC.local")
			table = NetworkTables.getTable("vision")
			table.putBoolean("vision", True)
		except:
			not DEBUG and print("NT not initialized")
			continue
		
		if None == table:
			try:
				table = NetworkTables.getTable("vision")
			except:
				not DEBUG and print("Table not initialized")
		if(DEBUG): break
	
	# Attempt to connect to a camera
	while cam==None:
		try:
			cam = cv2.VideoCapture(1)
			table.delete("camera_error")
			print("Camera operational!")
		except:
			try:
				table.putString("camera_error","Unable to connect the camera!")
			except:
				not DEBUG and print("NT not initialized at camera init fail")
			print("Camera not available!")
			time.sleep(1)
	
	# Main Loop
	while(1):
		# Precondition: NT is connected... we'll check on each op now too though
		
		# TODO periodically check and invalidate NetworkTables + Table if
		# The connection gets dropped
		# This should also set the enabled flag to false
		# One option is if (frame_counter % 20==0) or something
		# Another reasonable spot is in except block of getBoolean, 
		# Which should only happen if we lose our table.

		# Check if robot is enabled
		try:
			enabled = table.getBoolean("enabled", False)
		except:
			print('ERR: NT not connected...')
			if NetworkTables.isConnected():
				# The table handle is our problem
				table = NetworkTables.getTable("vision")
			else:
				# The actual connection is at fault
				# Try reconnecting
				NetworkTables.initialize(server='roboRIO-2811-FRC.local')
				table = NetworkTables.getTable("vision")
			continue
		
		if not enabled and not DEBUG:
			print("Robot not enabled...")

		#update our frame count
		frame_count+=1

		# Shove all image processing subroutine calls here
		try:
			# Get diff image
			valid,imgon,imgof = get_diff_sources()

			# Draw the diff if that's what you're into
			if valid and drawmode==DRAW_DIFF:
				try:
					cv2.imshow('diff', img)
					if cv2.waitKey(1) == 27:
						cv2.destroyAllWindows()
						break
				except:pass

			#If our worker thread is idle, break off and start 
			#processing a new image
			# TODO: check nice values, run below this priority
			# TODO: See how many parallel calculations we can run.
			#	we should be able to stream 2-3 threads across the Pi's cores
			#	to process things quickly.
			# TODO: Investigate using callbacks for NetworkTables publishing
			if process_thread.running():
				#print("Busy, skipping frame %i: %s" %frame_count,process_thread)
				pass
			elif process_thread.done():
				# Do something with the current results 
				print(process_thread.result())
				
				#restart the process with the newest image
				process_thread = process_pool.submit(image_process_pipeline,imgon,imgof,frame_count)
			else:
				print("????? Thread:%s"%process_thread)
				process_thread = process_pool.submit(image_process_pipeline,imgon,imgof,frame_count)
				
		except Exception as error:
			print("Ran into an error!")
			print(error)
			print(traceback.format_exc())

			#raise(error) #comment this line to continue running despite errors
			continue
			
		# Sleep a bit. This should help with some of the overheating issues,
		# as well as power draw.
		# TODO: investigate if this is required and/or causes problems
		#time.sleep(0.1)
		
	# Post cleanup!
	cv2.destroyAllWindows()
	GPIO.output(led_pin, False)
