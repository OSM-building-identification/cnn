import argparse
import numpy as np
from PIL import Image
from PIL import ImageDraw
import glob
import random

import predict

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--weights", help="weightfile", type=str)
args = parser.parse_args()

predict.load(args.weights)

images = glob.glob('data/tiles/*.jpg')
random.shuffle(images)

for imgpath in images:
	img = Image.open(imgpath)
	drw = ImageDraw.Draw(img, "RGBA")

	out = predict.predictMask(img)

	i = Image.fromarray(out)
	i.show()

	contours = predict.getContours(out)

	for pointset in contours:
		drw.polygon([(x,y) for [x, y] in pointset], outline=(0,255,255,158))

	img.show()

