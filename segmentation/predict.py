import os
import time
from keras.preprocessing import image
import numpy as np
from PIL import Image
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
from keras.models import *


import fcn


fcn.model.load_weights('best_seg.h5')

cwd = os.path.dirname(__file__)

imgpath = 'data/train_segmentation/tiles/26750_49792.jpg'

img = image.load_img(imgpath, target_size=(fcn.img_width, fcn.img_height))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = x * (1./255)
npimg = np.vstack([x]) 

out = fcn.model.predict(npimg, verbose=1)[0]
out = out.reshape(fcn.img_width, fcn.img_height)

# out[out<0.1] = 0
# out[out>=0.1]=1
out = out*255
i = Image.fromarray(out)
i.show()


# intermediate_layer_model = Model(inputs=fcn.model.input, outputs=fcn.model.get_layer('inout').output)
# ilayers = intermediate_layer_model.predict(npimg, verbose=1).reshape((1, 1024, 16, 16))[0]
# for layer in ilayers[1000:1020]:
# 	Image.fromarray(layer*255).show()