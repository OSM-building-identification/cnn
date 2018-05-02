# ------------------------------------------------------------------
#	Run the segmentation and contour prediction on all tiles to test
# ------------------------------------------------------------------
import argparse
import numpy as np
from PIL import Image
from PIL import ImageDraw
import glob
import random

import predict

# optionally accept a --weights argument to specify which weights to test
parser = argparse.ArgumentParser()
parser.add_argument("-w", "--weights", help="weightfile", type=str)
args = parser.parse_args()

# load or weights (or the default if none specified)
predict.load(args.weights)

# get all tiles, and shuffle their order
images = glob.glob('data/tiles/*.jpg')
random.shuffle(images)

for imgpath in images:
	# setup output image for drawing
	img = Image.open(imgpath)
	drw = ImageDraw.Draw(img, "RGBA")

	# get the mask, and display it
	out = predict.predictMask(img)
	i = Image.fromarray(out)
	i.show()

	# predict the contours
	contours = predict.getContours(out)

	# draw each contour as a cyan poly on top of the input image
	for pointset in contours:
		drw.polygon([(x,y) for [x, y] in pointset], outline=(0,255,255,158))

	# display the input image
	img.show()

