import os
import time
from keras.preprocessing import image
import numpy as np
from PIL import Image
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
from keras.models import *
import glob


import fcn


#fcn.model.load_weights('640.h5')

cwd = os.path.dirname(__file__)

imgpath = 'data/train_segmentation/tiles/27322_49764.jpg'

#checkpoints = [1,2,3,4,6,8,10,12,15,19,24,32,42,64,80,91,100,113,143,181,200,250,300,350,400,450,500,550,600,640]
checkpoints=[908,966,993]
img = image.load_img(imgpath, target_size=(fcn.img_width, fcn.img_height))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = x * (1./255)
npimg = np.vstack([x]) 

for checkpoint in checkpoints:
	fcn.model.load_weights('%s.h5' % checkpoint)

	out = fcn.model.predict(npimg, verbose=1)[0]
	out = out.reshape(fcn.img_width, fcn.img_height)

	# out[out<0.5] = 0
	# out[out>=0.5]=1
	out = out*255
	i = Image.fromarray(out)
	#i.show()
	i.convert('RGB').save('%s.jpg'%checkpoint)


# intermediate_layer_model = Model(inputs=fcn.model.input, outputs=fcn.model.get_layer('inout').output)
# ilayers = intermediate_layer_model.predict(npimg, verbose=1).reshape((1, 1024, 16, 16))[0]
# for layer in ilayers[1000:1020]:
# 	Image.fromarray(layer*255).show()