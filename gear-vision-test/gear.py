import cv2
import numpy as np
import grip
import glob
pipeline = grip.GearPipeline()

for image_path in glob.glob('*.png'):
	img = cv2.imread(image_path)
	print(pipeline.process(img))
	all_contours = pipeline.filter_contours_output
	meta = []
	for c in all_contours:
		area = cv2.contourArea(c)
		
		box =  cv2.boundingRect(c)
		x,y,w,h = box
		print("=====")
		print(area)
		print(w*h)
		center = (int(x+w/2),int(y+h/2))
		print(h/w)
		
		d={}
		d={
			'rect':w*h/area,
			'right_edge':x+w,
			'box':box,
			'height':h,
			'width':w,
			'center':center,
			'contour':c
			}
		meta.append(d)

	# Only keep things that are very rectanglular in nature
	rect_tolerance = 0.18
	meta = [x for x in meta if (1-rect_tolerance<x['rect']<1+rect_tolerance) ]
	for c in meta:
		print((c['rect'],c['box'],c['center']))

	# Only keep things that are about twice as tall as they are high.
	# Because of parrallax, things will likely be "thinner" as we near them or are to the side. 
	# However, the height will be fairly consistent. As a result, we'll never see something
	# with h/w ratio less than 2, although it might be somewhat greater.
	hw_tolerance=(1.9,3)
	meta = [x for x in meta if (hw_tolerance[0]<x['height']/x['width']<hw_tolerance[1]) ]

	# Draw all valid looking contours
	img2 = cv2.drawContours(img, [x['contour'] for x in meta], -1, (255,0,255), 3)

	# Select the right-most contour which will be our reference
	meta.sort(key=lambda x: x['center'][0],reverse = True)
	meta=meta[:1]

	#doodle!
	img2 = cv2.drawContours(img, [x['contour'] for x in meta], -1, (0,0,255), 3)

	# Do some calculations to find our best position
	# The loop structure is just to ensure it works sanely if there's 0 items
	robot_camera_offset = 6
	target = None
	for c in meta:
		one_inches_in_pixels = c['width']/2
		# Fudging scale to check things
		# The images are consistently off due to fisheye or some other
		# random thing, and this mostly adjusts for it in a single 
		# easy place.
		one_inches_in_pixels = one_inches_in_pixels*.85
		#
		target = c['right_edge'] + one_inches_in_pixels * robot_camera_offset
		target= int(target)
		cv2.line(img2, c['center'], (target,c['center'][1]), color=(0,0,255))
		cv2.line(img2, (target,0), (target,480), color=(0,0,255),thickness=5)
		
		# Draw the left-hand target for verification
		ref = int(c['center'][0] - one_inches_in_pixels * 8)
		cv2.line(img2, (ref,0), (ref,480), color=(0,255,0),thickness=3)

	# Draw our "Forward pixel"
	forward_pixel = 600
	cv2.line(img2, (forward_pixel,0), (forward_pixel,480), color=(255,0,0),thickness=3)

	# We now have a reference image, which is awesome! But what we really need is the 
	# offset angle. We can calculate this with the camera FOV
	fov_per_pixel = 50.2/640
	if target:
		error_angle = (forward_pixel-target)*fov_per_pixel
		text = "%0.2f" % error_angle
		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(img2,text,(10,60),font, 1,(255,255,255),2,cv2.LINE_AA)

	# Show the image
	# Hit escape to cycle
	while(1):
		cv2.imshow('diff w/ contours', img2)
		if cv2.waitKey(1) == 27: # Esc
			break
cv2.destroyAllWindows()
