'''
Simply display the contents of the webcam with optional mirroring using OpenCV 
via the new Pythonic cv2 interface.  Press <esc> to quit.
'''

import cv2

def show_webcam(mirror=False):
	cam = cv2.VideoCapture(0)
	while True:
		#TODO turn on lights
		lightson_ret, lightson_img = cam.read()
		# TODO: Turn off lights
		lightsoff_ret, lightsoff_img = cam.read()

		if not lightson_ret or not lightsoff_ret: 
			print "Invalid image!"
			continue

		if mirror: 
			#TODO: This doesn't need to be done except on diff, 
			#but this is easier to display as a test
			lightson_img = cv2.flip(lightson_img, 1)
			lightsoff_img = cv2.flip(lightsoff_img, 1)

		diff_img = cv2.subtract(lightson_img,lightsoff_img)

		cv2.imshow('my webcam', diff_img)
		if cv2.waitKey(1) == 27: 
			break  # esc to quit
	cv2.destroyAllWindows()

def main():
	show_webcam(mirror=True)

if __name__ == '__main__':
	main()
