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
    x = np.asarray(img).reshape((256, 256, 1))
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
    x = np.asarray(img)
    x = np.expand_dims(x, axis=0)
    x = x * (1./255)
    
    timgs.append(x)
nptileimgs = np.vstack(timgs) #tiles

data_gen_args = dict(
                     fill_mode='reflect',
                     shear_range=0.1,
                     rotation_range=90.,
                     width_shift_range=0.1,
                     height_shift_range=0.1,
                     zoom_range=0.2)
image_datagen = image.ImageDataGenerator(**data_gen_args)
mask_datagen = image.ImageDataGenerator(**data_gen_args)
seed = 1
image_datagen.fit(nptileimgs[:10], augment=True, seed=seed)
mask_datagen.fit(npimgs[:10], augment=True, seed=seed)

image_generator = image_datagen.flow(nptileimgs, seed=seed)
mask_generator = mask_datagen.flow(npimgs, seed=seed)


batchnum=0
for e in range(10):
    print('Epoch', e)
    batches = 0
    while batches < 64:
        image_batch = image_generator.next()
        mask_batch = mask_generator.next()

        # Image.fromarray((image_batch[0]*255).astype(np.uint8), 'RGB').show()
        # Image.fromarray((mask_batch[0].reshape((256,256))*255).astype(np.uint8)).show()
        fcn.model.fit(image_batch, mask_batch,batch_size=4, verbose=1)
        batches += 1
        batchnum += 1
	fcn.model.save_weights('%s.h5'%batchnum)


# fcn.model.fit(nptileimgs, npimgs, batch_size=4, nb_epoch=10, verbose=1, validation_split=0.2, shuffle=True)
# fcn.model.save_weights('out.h5')
