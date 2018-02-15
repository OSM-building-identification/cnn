import os
import time
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as K
from keras.preprocessing import image
import numpy as np
import cnn
from PIL import Image
from matplotlib import pyplot as plt
from vis.visualization import visualize_activation
from vis.utils import utils
from vis.input_modifiers import Jitter
from keras import activations
import scipy.misc

model = cnn.model
model.load_weights('./best.h5')
layer_idx = utils.find_layer_idx(model, 'preds')
model.layers[layer_idx].activation = activations.linear
model = utils.apply_modifications(model)

img = image.load_img('data/test/False/26876_49785.jpg', target_size=(cnn.img_width, cnn.img_height))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = x * (1./255)

for filter_idx in range(1):
	img = visualize_activation(model, layer_idx, filter_indices=filter_idx, seed_input=x, max_iter=30)
	scipy.misc.toimage(img, cmin=0.0, cmax=255.0).save('%s.jpg' % filter_idx)
