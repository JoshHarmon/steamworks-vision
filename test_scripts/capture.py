'''
Simply display the contents of the webcam using OpenCV cv2 interface

Pr
Press <esc> to quit.
'''

import cv2
import numpy
import os
frame = 1
mirror = False

if __name__ == '__main__':
	starting_distance = input('Starting distance (inches): ')
	increment_distance = input('Distance change per frame: ')
	
	starting_distance = float(starting_distance)
	increment_distance = float(increment_distance)
	
	current_dis = starting_distance
	
	cam = cv2.VideoCapture(0)
	while True:
		try:
			ret_val, img = cam.read()
			if mirror: 
				img = cv2.flip(img, 1)
			if ("--show" in sys.argv or "-s" in sys.argv):
				cv2.imshow('my webcam', img)
				key=cv2.waitKey(1)
				if key == 27:
					#escape to exit
					break
				if key == 32:
					#space to save a screenshot
					current_dis = current_dis - increment_distance
					name=os.getcwd()+"/frame_%02s-%02s.png" % (frame, current_dis)
					print(name)
					cv2.imwrite(name,img)
					frame+=1
		except KeyboardInterrupt:
				current_dis = current_dis - increment_distance
				name=os.getcwd()+"/frame_%02s-%02s.png" % (frame, current_dis)
				print(name)
				cv2.imwrite(name,img)
				frame+=1				
	cv2.destroyAllWindows()
