import os
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as K
from keras.preprocessing import image
import numpy as np
import cnn
from PIL import Image

cwd = os.path.dirname(__file__)

dir_path = os.path.join(cwd, '..', 'data/train/False/')
cnn.model.load_weights(os.path.join(cwd, 'best.h5'))
images = os.listdir(dir_path)
failed = 0
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

print "%s failed of %s" % (failed, len(images))
