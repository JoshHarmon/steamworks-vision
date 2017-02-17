"""
2017 Steamworks vision code for Team 2811 (StormBots)
"""

import cv2
import numpy as np
from grip import GripPipeline

import os
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


from networktables import NetworkTables
import logging

import time
import sys
import math

cam = cv2.VideoCapture(0)


def main():
	bad_data = False

	#text_file = open("Output.txt", "w")

	grip = GripPipeline()

	##NetworkTables.initialize(server='roboRIO-2811-FRC.local')

	##table = NetworkTables.getTable("contourData")
	while True:
		start_time = time.time()
		ret_val, img = cam.read()
		contours = False

		if ret_val:
			img = get_diff(mirror=False)
						
			
			grip.process(img)
			bad_data = False

			contours = grip.filter_contours_output

			img2 = cv2.drawContours(img, contours, -1, (0,255,0), 3)
			cv2.imshow('test', img2)
			if cv2.waitKey(1) == 27:
                                break # esc to quit
						
			print('# contours:', len(contours))
			dArr = []

			for i in range(len(contours)):

				moments1 = cv2.moments(contours[i])

				cx = int(moments1['m10']/moments1['m00'])
				cy = int(moments1['m01']/moments1['m00'])

				area = cv2.contourArea(contours[i])

				dArr.append([i, cx, cy, area])
				
				#text_file.write("%d %d %d %d %d\n" % (i, cx, cy, area, count))

			dArr.sort(key=lambda x: x[3], reverse=True)

			## dArr = [[1, 419, 140, 11317.0], [0, 215, 142, 10963.0], [2, 550, 300, 12000.0], [4, 650, 200, 8491.0], [5, 200, 100, 7540.0]]

			##print(dArr)
			
			## Traits: Group Height, dTop, LEdge, Width ratio, Height ratio

			traitAnalysisArr = []
			print(len(dArr))
			for i in range(len(dArr) - 1): ## range stops before the length, so this stays in bounds
				##print('outer idx is', i, ' with list length of', len(dArr))
				for j in range(i + 1, len(dArr)):
					##print('inner idx is', j, ' with list length of', len(dArr))

					## The non-2 values should represent the top target (as we sort dArr by area and the top target is bigger)
					## The -2 values, logically, represent the bottom target rect values
					##print('getting rect i for idx', dArr[i][0], 'of contours list with max idx of', (len(contours) - 1))
					x,y,w,h = cv2.boundingRect(contours[dArr[i][0]])  ## dArr[i][0] represents the true i-value of the contour
					##print('getting rect j for idx', dArr[j][0], 'of contours list with max idx of', (len(contours) - 1))
					x2,y2,w2,h2 = cv2.boundingRect(contours[dArr[j][0]])

					##groupHeightTestValue = (h/((y2+h2-y)*.4)) ## Top target ~ 40% total cluster height

					##dTopTestValue = abs((y2 - y)/(((y2 + h2) - y)*0.6)) ## Top of bot to top of top ~ 60% total cluster height

					## See how well the left edges of the targets line up
					lEdgeTestValue = abs((((x - x2) / w) + 1))

					## Note that these ratios are not safe until we've
					## iterated based on greatest-least area... this may
					## involve getting i from (sorted) dArr and fetching that i from
					## the contours list
					widthCompareTestValue = abs((w / w2)) ## Widths should be about the same
					heightCompareTestValue = abs((h / (2*h2))) ## Top should be about twice as tall as bottom

					areaCompareValue = abs(((w * h) / (w2 * h2)) - 2) ## .5 or (2) (need to force one later)

					totalTestScore = lEdgeTestValue + widthCompareTestValue + heightCompareTestValue + areaCompareValue

					traitAnalysisArr.append([i, j, totalTestScore])
			
			## end traits loop
			bestIdx = 0
			bestScore = sys.maxsize
			if (len(traitAnalysisArr) > 0):
				for i in range(len(traitAnalysisArr)):
					if (traitAnalysisArr[i][2] < bestScore):
						bestIdx = i
						bestScore = traitAnalysisArr[i][2]
				print('Best score: pair', traitAnalysisArr[i], 'with a score of', traitAnalysisArr[i][2], '')
				print('   ^ Contour 1: ', dArr[traitAnalysisArr[i][0]], ' || Contour 2: ', dArr[traitAnalysisArr[i][1]])

				##table.putNumberArray("coordinates", dArr[0][1:]) ## cx and cy pushed to NT

				print(get_distance_to_boiler(dArr[traitAnalysisArr[i][0]][1]))
			else:
				print('Analysis failed...')
		else:
			print('Pipeline returned an error')
			bad_data = True
		end_time = time.time()
	#text_file.close()
	cv2.destroyAllWindows()
	GPIO.output(led_pin, False)

		##print((end_time - start_time) * 1000)

'''
Conditions for boiler targeting
len(contours) >= 2
two targets_vertically_stacked


'''

'''
Conditions for gear peg targeting
len(contours) >= 2    (3 if one is split by the peg)

if split, targets_vertically_stacked for one of the physical targets ( two contours )


'''

def get_diff(mirror=False):
	GPIO.output(led_pin, True)
	time.sleep(.05)
	lightson_ret, lightson_img = cam.read()
	GPIO.output(led_pin, False)
	time.sleep(.05)
	lightsoff_ret, lightsoff_img = cam.read()
	#GPIO.output(led_pin, True)

	if not lightson_ret or not lightsoff_ret: 
		print("Invalid image!")
		# This should probably just return a black image 
		# of an appropriate size 
		# (or a really small image that just process as nothing instantly)
		# Alternatively, we can return a tuple with (validity,image)
		height=1
		width=1
		return numpy.zeros((height,width,3), numpy.uint8)

	diff_img = cv2.subtract(lightsoff_img, lightson_img)
	
	if mirror: 
		diff_img = cv2.flip(diff_img, 1)
		
	return diff_img

def get_distance_to_boiler(target_cy):

        ## TODO: Optimize to use FOV in rad to remove the conversion
        ## TODO: Optimize to get cx as either arg or pass in dArr item
        
        target_height = 8 + (2/12.0)  - (42/12.0)   # approx height of top target (trig: opp) !!!! MINUS THE CAMERA TEST HEIGHT VALUE !!!!

        # The angle the camera is tilted *back* at. Center pixel represents this angle.
        camera_angle = 20.0

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

        total_angle_rad = total_angle * (math.pi / 180.0)

        distance = target_height / math.tan(total_angle_rad)

        return distance

def get_horizontal_angle_offset(target_cx):
        ## TODO: Optimize to get cx as arg or get dArr value

        degrees_per_px = 1 / 12.30355

        angle_offset = degrees_per_px * (target_cx - 320)

        return angle_offset

        
def targets_horizontally_stacked(contour1, contour2):
	moments1 = cv2.moments(contour1)
	moments2 = cv2.moments(contour2)

	cy1 = int(moments1['m01']/moments1['m00'])
	cy2 = int(moments2['m01']/moments2['m00'])

	return abs(cy1 - cy2) < 12

def targets_vertically_stacked(contour1, contour2):
	moments1 = cv2.moments(contour1)
	moments2 = cv2.moments(contour2)

	cx1 = int(moments1['m10']/moments1['m00'])
	cx2 = int(moments2['m10']/moments2['m00'])

	return abs(cx1 - cx2) < 12

if __name__ == '__main__':
	main()
