import os
import time
from keras.preprocessing import image
import numpy as np
from PIL import Image
from keras.callbacks import ModelCheckpoint, LearningRateScheduler


import fcn

cwd = os.path.dirname(__file__)

masks_path = 'data/train_segmentation/train/masks'
masks = os.listdir(masks_path)

imgs = []
for imgPath in masks:
    img = image.load_img(os.path.join(masks_path, imgPath), target_size=(fcn.img_width, fcn.img_height), grayscale = True)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x * (1./255)
    x[x > 0.5] = 1
    x[x <= 0.5] = 0
    
    imgs.append(x)
npimgs = np.vstack(imgs) #masks

tiles_path = 'data/train_segmentation/train/tiles'
tiles = os.listdir(tiles_path)

timgs = []
for imgPath in tiles:
    img = image.load_img(os.path.join(tiles_path, imgPath), target_size=(fcn.img_width, fcn.img_height))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x * (1./255)
    
    timgs.append(x)
nptileimgs = np.vstack(timgs) #tiles

model_checkpoint = ModelCheckpoint('unet.hdf5', monitor='loss',verbose=1, save_best_only=True)
fcn.model.fit(nptileimgs, npimgs, batch_size=4, nb_epoch=10, verbose=1, validation_split=0.2, shuffle=True, callbacks=[model_checkpoint])