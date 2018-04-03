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


import fcn

print "loading weights..."
fcn.model.load_weights('data/weights/267.h5')

cwd = os.path.dirname(__file__)

#imgpath = 'data/train_segmentation/tiles/20987_45730.jpg' #20745_46208, 24659_52516, 27322_49764

images = glob.glob('data/hires-tiles/*.jpg')
random.shuffle(images)

for imgpath in images:
	img = image.load_img(imgpath, target_size=(fcn.img_width, fcn.img_height))
	#img.show()
	x = image.img_to_array(img)
	x = np.expand_dims(x, axis=0)
	x = x * (1./255)
	npimg = np.vstack([x]) 

	out = fcn.model.predict(npimg, verbose=1)[0]
	out = out.reshape(fcn.img_width, fcn.img_height)

	# out[out<0.5] = 0
	# out[out>=0.5]=1
	out = out*255
	i = Image.fromarray(out)
	i.show()

	rst,thresh = cv2.threshold(out.astype(np.uint8),158,255,0)#cv2.adaptiveThreshold(img, 255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C, thresholdType=cv2.THRESH_BINARY, blockSize=7, C=0)
	(x, contours, hier) = cv2.findContours(thresh, 1, cv2.CHAIN_APPROX_SIMPLE)
	print cv2.CHAIN_APPROX_SIMPLE

	drw = ImageDraw.Draw(img, "RGBA")

	for contour in contours:
		rect = cv2.minAreaRect(contour)
		box = cv2.boxPoints(rect)
		boxpts = [(p[0], p[1]) for p in box]
		epsilon = 0.01*cv2.arcLength(contour,True)
		approx = cv2.approxPolyDP(contour,epsilon,True)
		approxpnts = [(p[0][0], p[0][1]) for p in contour]


		drw.polygon(boxpts, outline=(255,0,0,158))
		drw.polygon(approxpnts, outline=(0,0,255,158))
		# try:
			
		# except TypeError:
		# 	print "draw err"


	img.show()


# intermediate_layer_model = Model(inputs=fcn.model.input, outputs=fcn.model.get_layer('inout').output)
# ilayers = intermediate_layer_model.predict(npimg, verbose=1).reshape((1, 1024, 16, 16))[0]
# for layer in ilayers[1000:1020]:
# 	Image.fromarray(layer*255).show()