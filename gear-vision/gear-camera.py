import cv2
import numpy as np
import grip

from networktables import NetworkTables
from socket import error as SocketError
import errno

pipeline = grip.GearPipeline()

NetworkTables.initialize(server='roboRIO-2811-FRC.local')

frame_count = 0

camera = cv2.VideoCapture(0)

num_nt_failures = 0
rio_last_heartbeat = -1

table = NetworkTables.getTable("vision")

while True:
	frame_count += 1
	ret_val, img = camera.read()
	
	if not ret_val:
		# Weren't able to get an image...
		# We'll just fail semi-silently here, outputting no data
		# This needs to catch us before we try to process img
		continue
	
	print(pipeline.process(img))
	all_contours = pipeline.filter_contours_output
	meta = []
	for c in all_contours:
		area = cv2.contourArea(c)
		
		box =  cv2.boundingRect(c)
		x,y,w,h = box
		#print("=====")
		#print(area)
		#print(w*h)
		center = (int(x+w/2),int(y+h/2))
		#print(h/w)
		
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
	
	if NetworkTables.isConnected():
		# Get the preference value from networktables
		# And if that doesn't work, just keep our current value
		rect_tolerance = table.getNumber("pref_rect_tolerance", rect_tolerance)
	
	meta = [x for x in meta if (1-rect_tolerance<x['rect']<1+rect_tolerance) ]
	for c in meta:
		print((c['rect'],c['box'],c['center']))

	# Only keep things that are about twice as tall as they are high.
	# Because of parrallax, things will likely be "thinner" as we near them or are to the side. 
	# However, the height will be fairly consistent. As a result, we'll never see something
	# with h/w ratio less than 2, although it might be somewhat greater.
	hw_tolerance=[1.9,3]
	
	if NetworkTables.isConnected():
		hw_tolerance[0] = table.getNumber("pref_hw_tolerance_low", hw_tolerance[0])
		hw_tolerance[1] = table.getNumber("pref_hw_tolerance_high", hw_tolerance[1])
	
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
		ff = 0.85
		if NetworkTables.isConnected():
			ff = table.getNumber("pref_ff", 0.85)

		one_inches_in_pixels = one_inches_in_pixels * ff

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
		if NetworkTables.isConnected():
			try:
				#table = NetworkTables.getTable("vision");
				table.putNumber("gear_error_angle", error_angle)
				table.putNumber("gear_frame_number", frame_count)
				print("Yay! Posted to NetworkTables!")
			except:
				print("Values not posted to NT.")
				# try connecting again so that things might work next time.
				# this might not be the best solution though; if networktables
				# feels that it's still connected, even when it isn't, it will
				# throw an exception if you call initialize() again
				if not NetworkTables.isConnected():
					NetworkTables.initialize(server='roboRIO-2811-FRC.local')
		
		text = "%0.2f" % error_angle
		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(img2,text,(10,60),font, 1,(255,255,255),2,cv2.LINE_AA)
	
	# Aaaand now the heartbeat check fun begins...
	if NetworkTables.isConnected():
		try:
			sdtable = NetworkTables.getTable("SmartDashboard")
			sdtable.putNumber("raspi_heartbeat", frame_count)
			print("Sent heartbeat...")
			
			# Now see if we're still connected to the RIO
			# Even with NetworkTables apparently trying to cache things,
			# we can determine if things are still connected based on if
			# the RIO's heartbeat value updates. If we go offline, the value
			# can't possibly update.
			rio_heartbeat = sdtable.getNumber("rio_heartbeat", -1)

			if (rio_heartbeat > rio_last_heartbeat):
				print("Probably connected... (%d vs %d)" % (rio_heartbeat, rio_last_heartbeat))

				if (num_nt_failures > 0):
					print("... After %d failures" % num_nt_failures)
					# clear NT failures counter
					num_nt_failures = 0
				rio_last_heartbeat = rio_heartbeat
			elif (rio_heartbeat == rio_last_heartbeat):
				print("Possibly disconnected - RIO heartbeat unchanged")

				if (num_nt_failures > 0):
					print("... After %d failures" % num_nt_failures)
				# add to failures counter, as this is a potential problem
				num_nt_failures += 1
			else:
				print("Possibly reconnected/reset (%d vs %d)" % (rio_heartbeat, rio_last_heartbeat))
				if (num_nt_failures > 0):
					print("Failure %d")
				num_nt_failures += 1
		except SocketError as e:
			if e.errno != errno.ECONNRESET: # Usually happens if the RIO goes offline then comes back
				raise # Not error we are looking for
				print("Socket error (but not conn reset) caught...")
			# Handle error here
			print("Connection reset caught... RIO may have come back online...")
		except:
			print("Failed to send heartbeat... Perhaps we're disconnected?")
	else:
		print("NetworkTables isn't even connected... :(")
	# Show the image
	#cv2.imshow('gear view', img2)
	#if cv2.waitKey(1) == 27: # Esc
	#	break
#cv2.destroyAllWindows()
