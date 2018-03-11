import sys
sys.path.append('./util/')

import os
import time
from keras.preprocessing import image
import numpy as np
from PIL import Image
import cv2
from PIL import ImageDraw
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
from keras.models import *
import glob
import random
from cStringIO import StringIO


import fcn
import naip


print "loading weights..."
fcn.model.load_weights('data/weights/993.h5')

def findContours(x,y,z):
	(startX, startY) = naip.tile2deg(x,y,z)
	(endX, endY) = naip.tile2deg(x+1,y+1,z)
	dx = endX-startX
	dy = endY-startY

	img = naip.fetchTile(x,y,z)
	if img == None:
		return False
	if img != None:
		try:
			file_jpgdata = StringIO(img)
			i = Image.open(file_jpgdata)
		except IOError:
			return 

		arr = image.img_to_array(i)
		arr = np.expand_dims(arr, axis=0)
		arr = arr * (1./255)

		npimg = np.vstack([arr]) 
		out = fcn.model.predict(npimg, verbose=1)[0]
		out = out.reshape(fcn.img_width, fcn.img_height)
		out = out*255
		# i = Image.fromarray(out)
		# i.show()

		rst,thresh = cv2.threshold(out.astype(np.uint8),158,255,0)
		(x, contours, hier) = cv2.findContours(thresh, 1, cv2.CHAIN_APPROX_SIMPLE)
		
		realcontours = []
		for contour in contours:
			rect = cv2.minAreaRect(contour)
			box = cv2.boxPoints(rect)
			realContour = [[((coord[0]/255)*dx)+startX, ((coord[1]/255)*dy)+startY] for coord in box]
			realcontours.append(realContour)
		return realcontours

# x = 27200
# y = 49596
# z = 17
# print findContours(x,y,z)
