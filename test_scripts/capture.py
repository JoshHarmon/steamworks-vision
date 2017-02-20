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
	cam = cv2.VideoCapture(1)
	while True:
		ret_val, img = cam.read()
		if mirror: 
			img = cv2.flip(img, 1)
		cv2.imshow('my webcam', img)
		key=cv2.waitKey(1)
		if key == 27:
			#escape to exit
			break
		if key == 32:
			#space to save a screenshot
			name=os.getcwd()+"/frame_%02s.png" % frame
			print name
			cv2.imwrite(name,img)
			frame+=1
	cv2.destroyAllWindows()
