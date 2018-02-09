import os
import time
from keras.preprocessing import image
import numpy as np
from PIL import Image
from keras.callbacks import ModelCheckpoint, LearningRateScheduler


import fcn


fcn.model.load_weights('out.h5')

cwd = os.path.dirname(__file__)

imgpath = 'data/train_segmentation/train/tiles/27213_49614.jpg'

img = image.load_img(imgpath, target_size=(fcn.img_width, fcn.img_height))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = x * (1./255)
npimg = np.vstack([x]) 

out = fcn.model.predict(npimg, verbose=1)[0]
print out;
out = out.reshape(fcn.img_width, fcn.img_height)
out = out*255
i = Image.fromarray(out)
i.show()
