import numpy as np
from PIL import Image
from PIL import ImageDraw
import glob
import random

import predict

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
		drw.polygon([(x,y) for [x, y] in pointset], outline=(0,200,0,158))

	img.show()

