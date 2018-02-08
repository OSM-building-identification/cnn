from keras.layers import *
from keras import backend as K
from keras.models import *
from keras.regularizers import l2
from keras.optimizers import *
from keras.preprocessing import image
import numpy as np

from resnethelp import *
from bilen import *

img_width, img_height = 256, 256

input_shape = (img_width, img_height, 3)

inputs = Input(input_shape)
weight_decay=0
bn_axis = 3

x = Conv2D(64, (7, 7), strides=(2, 2), padding='same', name='conv1', kernel_regularizer=l2(weight_decay))(inputs)
x = BatchNormalization(axis=bn_axis, name='bn_conv1')(x)
x = Activation('relu')(x)
x = MaxPooling2D((3, 3), strides=(2, 2))(x)

x = conv_block(3, [64, 64, 256], stage=2, block='a', strides=(1, 1))(x)
x = identity_block(3, [64, 64, 256], stage=2, block='b')(x)
x = identity_block(3, [64, 64, 256], stage=2, block='c')(x)

x = conv_block(3, [128, 128, 512], stage=3, block='a')(x)
x = identity_block(3, [128, 128, 512], stage=3, block='b')(x)
x = identity_block(3, [128, 128, 512], stage=3, block='c')(x)
x = identity_block(3, [128, 128, 512], stage=3, block='d')(x)

x = conv_block(3, [256, 256, 1024], stage=4, block='a')(x)
x = identity_block(3, [256, 256, 1024], stage=4, block='b')(x)
x = identity_block(3, [256, 256, 1024], stage=4, block='c')(x)
x = identity_block(3, [256, 256, 1024], stage=4, block='d')(x)
x = identity_block(3, [256, 256, 1024], stage=4, block='e')(x)
x = identity_block(3, [256, 256, 1024], stage=4, block='f')(x)

x = conv_block(3, [512, 512, 2048], stage=5, block='a')(x)
x = identity_block(3, [512, 512, 2048], stage=5, block='b')(x)
x = identity_block(3, [512, 512, 2048], stage=5, block='c')(x)
#classifying layer
x = Conv2D(1, (1, 1), kernel_initializer='he_normal', activation='linear', padding='valid', strides=(1, 1), kernel_regularizer=l2(weight_decay))(x)

x = BilinearUpSampling2D(size=(32, 32))(x)

model = Model(inputs, x)
model.load_weights('data/resnet50_weights_tf_dim_ordering_tf_kernels.h5', by_name=True)
model.compile(optimizer = Adam(lr = 1e-4), loss = 'binary_crossentropy', metrics = ['accuracy'])