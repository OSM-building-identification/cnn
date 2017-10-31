import os
import keras
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as K
import cnn

cwd = os.path.dirname(__file__)

train_data_dir = os.path.join(cwd, '..', 'data/train')
validation_data_dir = os.path.join(cwd, '..', 'data/test')
nb_train_samples = 20000
nb_validation_samples = 100
epochs = 100
batch_size = 16

 
class Callbacks(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        self.model.save_weights(os.path.join(cwd, '..', 'weights%s.h5' % epoch))
        return

callbacks = Callbacks()


train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True)

test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(cnn.img_width, cnn.img_height),
    batch_size=batch_size,
    class_mode='binary')

validation_generator = test_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(cnn.img_width, cnn.img_height),
    batch_size=batch_size,
    class_mode='binary')

cnn.model.fit_generator(
    train_generator,
    steps_per_epoch=nb_train_samples // batch_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=nb_validation_samples // batch_size,
    #class_weight={0:1,1:0.5},
    callbacks=[callbacks])