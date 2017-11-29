import os
from PIL import Image

dir_path = 'data/test/True'
images = os.listdir(dir_path)
count = int(len(images)**0.5)
for i, imgPath in enumerate(images):
	row = i/count
	print (imgPath, int(((float(i)/count)-row)*count))