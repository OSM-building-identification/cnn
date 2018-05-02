import sys
sys.path.append('./util/')

from keras.preprocessing import image
import numpy as np
import cv2

import fcn
import contourMath
print "loading weights..."
fcn.model.load_weights('./data/weights/segmentation.h5')

def predictMask(arr):
	arr = np.expand_dims(arr, axis=0)
	arr = arr * (1./255)
	npimg = np.vstack([arr]) 
	out = fcn.model.predict(npimg, verbose=1)[0]
	out = out.reshape(fcn.img_width, fcn.img_height)
	out = out*255
	return out

def getContours(i):
	mask = image.img_to_array(i)
	rst,thresh = cv2.threshold(mask.astype(np.uint8),138,255,0)
	(x, contours, hier) = cv2.findContours(thresh, 1, cv2.CHAIN_APPROX_NONE)
	
	outcontours = []
	for contour in contours:
		rect = cv2.minAreaRect(contour)
		box = cv2.boxPoints(rect)
		boxpts = [[p[0], p[1]] for p in box]
		peri = cv2.arcLength(contour,True)
		if peri > 20:
			contourpnts = [[p[0][0], p[0][1]] for p in contour]
			contourpnts = contourpnts[::-1]

			lineIndicies = []
			residualsThresh = 2
			startindex=0
			endindex=2

			points = []

			while startindex < len(contourpnts)-1:
				thesepoints = contourpnts[startindex:endindex]

				xs = [x for (x,y) in thesepoints]
				ys = [y for (x,y) in thesepoints]

				if len(set(xs)) > 1:
					z, residuals, rank, singular_values, rcond = np.polyfit(xs, ys, 1, full=True)
				else:
					residuals = 0

				seglen = np.linalg.norm(np.array(contourpnts[startindex])-np.array(contourpnts[endindex-1]))
				if residuals > residualsThresh or endindex >= len(contourpnts)-1:
					if(seglen > 10):
						if len(lineIndicies) > 0:
							prevLine = lineIndicies[-1]
							inbetween = contourpnts[prevLine[1]:startindex]
							theta = contourMath.getSegmentAngle([contourpnts[prevLine[0]], contourpnts[prevLine[1]]])
							if len(inbetween) > 2:
								shull = contourMath.sharpHull(theta, inbetween)
								points = points+shull
						else:
							contourpnts += contourpnts[:startindex]
						points = points+contourpnts[startindex:endindex-1]
						lineIndicies.append([startindex, endindex-1])
					startindex = endindex
					endindex = startindex+2
				else:
					endindex += 1

			if len(lineIndicies)  > 0:
				prevLine = lineIndicies[-1]
				theta = contourMath.getSegmentAngle([contourpnts[prevLine[0]], contourpnts[prevLine[1]]])
				tail = contourpnts[prevLine[1]:]
				shull = contourMath.sharpHull(theta, tail)
				points = points+shull

			if True or len(points) < 3 or len(lineIndicies) == 0:
				pointset = boxpts
			else:
				pointset = points
				epsilon = 1
				pointset = cv2.approxPolyDP(np.array(pointset),epsilon,True)
				pointset = [[p[0][0], p[0][1]] for p in pointset]

			outcontours.append(pointset)
	
	return outcontours