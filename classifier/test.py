import argparse
import os
import time
from keras.preprocessing import image
import numpy as np
from PIL import Image

import cnn

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--weights", help="weightfile", type=str, default='./data/weights/classifier.h5')
args = parser.parse_args()

cwd = os.path.dirname(__file__)

dir_path = 'data/train_classifier/train/False'
cnn.model.load_weights(args.weights)
images = os.listdir(dir_path)
failed = 0
totalTime = 0
for imgPath in images:
	img = image.load_img(os.path.join(dir_path, imgPath), target_size=(cnn.img_width, cnn.img_height))
	x = image.img_to_array(img)
	x = np.expand_dims(x, axis=0)
	x = x * (1./255)
	imgs = np.vstack([x])
	classes = cnn.model.predict_classes(imgs, batch_size=10, verbose=0)

	if classes[0][0] == 1:
		failed = failed + 1
		img = Image.open(os.path.join(dir_path, imgPath))
		img.show() 
		print imgPath, classes[0][0]
	else:
		print imgPath

print "%s failed of %s. %s percent acc" % (failed, len(images), round(((1-(float(failed)/len(images)))*100), 3) )