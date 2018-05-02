# ------------------------------------------------------------------
#	Predict the contours in an image using FCN + contour appoximation
# ------------------------------------------------------------------
import sys
sys.path.append('./util/')

from keras.preprocessing import image
import numpy as np
import cv2

import fcn
import contourMath

# call to load the weights with whatever you want
def load(weights):
	if not weights:
		weights = './data/weights/segmentation.h5'
	print "loading weights..."
	fcn.model.load_weights(weights)

# predict the image mask of an input image 'arr', by running it though the model
def predictMask(arr):
	arr = np.expand_dims(arr, axis=0)
	arr = arr * (1./255)
	npimg = np.vstack([arr]) 
	out = fcn.model.predict(npimg, verbose=1)[0]
	out = out.reshape(fcn.img_width, fcn.img_height)
	out = out*255
	return out

# takes in an image mask (probably from predictMask) and:
# returns an array of contours, one for each building
def getContours(i):
	# use opencv to find a threshold and find the unapproximated contours
	mask = image.img_to_array(i)
	rst,thresh = cv2.threshold(mask.astype(np.uint8),138,255,0)
	(x, contours, hier) = cv2.findContours(thresh, 1, cv2.CHAIN_APPROX_NONE)
	
	# for each contour find its straight lined concave approximation
	outcontours = []
	for contour in contours:
		# find the fitted containing bounding box for the contour
		rect = cv2.minAreaRect(contour)
		box = cv2.boxPoints(rect)
		boxpts = [[p[0], p[1]] for p in box]

		# calculate the perimiter of the contour and ignore those that are too small
		peri = cv2.arcLength(contour,True)
		if peri > 20: #20px long perimiter is our cutoff
			contourpnts = [[p[0][0], p[0][1]] for p in contour] 
			# reverse the direction of the contour points, opencv returns clockwise, but we want counter-clock
			contourpnts = contourpnts[::-1]

			# threshold of residuals for a subset of the contour to be considered a straight enough line
			residualsThresh = 0.5
			
			# start and end indicies of the current subset of the contour
			startindex=0
			endindex=2

			lineIndicies = [] # all previous straight lines that have been found
			points = [] 			# output points from connecting straight lines

			# keep finding straight lines untill we hit the end of the contour
			while startindex < len(contourpnts)-1:
				thesepoints = contourpnts[startindex:endindex] #current subset of the contour we are examining

				# find a linear fit for the subset of the contour
				xs = [x for (x,y) in thesepoints]
				ys = [y for (x,y) in thesepoints]
				# if handles vertical lines, otherwise fit would fail
				if len(set(xs)) > 1:
					z, residuals, rank, singular_values, rcond = np.polyfit(xs, ys, 1, full=True)
				else:
					residuals = 0
				# find the length of the segment
				seglen = np.linalg.norm(np.array(contourpnts[startindex])-np.array(contourpnts[endindex-1]))
				
				# if we have exceeded the residuals threshold, or hit the end of contour, we fininsh the line
				if residuals > residualsThresh or endindex >= len(contourpnts)-1:
					# ignore "straight lines" that don't have enough points to be meaningful
					if(seglen > 10):
						# if this isn't the first line, find the "sharp hull" that connects them
						if len(lineIndicies) > 0:
							prevLine = lineIndicies[-1]
							# points in between the two lines
							inbetween = contourpnts[prevLine[1]:startindex]
							# angle of the previous line
							theta = contourMath.getSegmentAngle([contourpnts[prevLine[0]], contourpnts[prevLine[1]]])
							# if the lines are separated by more than two points, connect them with a sharpHull
							if len(inbetween) > 2:
								shull = contourMath.sharpHull(theta, inbetween)
								points = points+shull # add the hull to the points
						else: 
							# if this is the first line, append all the points leading 
							# up to the start of this line on the end of the contour, so that the loop will close
							contourpnts += contourpnts[:startindex]
						points = points+contourpnts[startindex:endindex-1] #add the straight line to the final contour
						lineIndicies.append([startindex, endindex-1])
					# start finding the next line starts at the end of this line, and is at least 2 long
					startindex = endindex
					endindex = startindex+2
				else: #otherwise we hypothesize that the line continues
					endindex += 1

			# after all lines have been found, try to close the loop with a sharpHull, back to the first Line
			if len(lineIndicies)  > 0:
				prevLine = lineIndicies[-1]
				theta = contourMath.getSegmentAngle([contourpnts[prevLine[0]], contourpnts[prevLine[1]]])
				tail = contourpnts[prevLine[1]:]
				shull = contourMath.sharpHull(theta, tail)
				points = points+shull

			# if we don't have any straight lines, or not enough points in the contour approximate as a box
			if len(points) < 3 or len(lineIndicies) == 0:
				pointset = boxpts
			else:
				# otherwise run a simple approximation to, clean up the output and use our connected straight lines
				pointset = points
				epsilon = 2
				pointset = cv2.approxPolyDP(np.array(pointset),epsilon,True)
				pointset = [[p[0][0], p[0][1]] for p in pointset]

			# add this contour or box to the result list of contours
			outcontours.append(pointset)
	
	return outcontours