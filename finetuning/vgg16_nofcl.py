from keras.applications.vgg16 import VGG16
from keras.layers import Dense
from keras.models import Model
from keras.optimizers import SGD


import numpy as np 
import load

vgg16 = VGG16(weights='imagenet', include_top=True)
 
#pop out softmax
x = Dense(8, activation='softmax', name='predictions')(vgg16.layers[-2].output)
model = Model(input=vgg16.input, output=x)
model.summary()

for layer in model.layers[:10]:
       layer.trainable = False

sgd = SGD(lr=1e-3, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(optimizer=sgd, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

print("Done loading VGG16")



(X_train, Y_train), (X_valid, Y_valid) = load.load_data()
print("Finish loading NAIP images")

#Model info 
img_rows, img_cols = 224, 224 # Resolution of NAIP inputs
channel = 3                   # RGB 
num_classes = 2
batch_size = 16 
nb_epoch = 5

model.fit(np.array(X_train), np.array(Y_train),
          batch_size=batch_size,
          epochs=nb_epoch,
          shuffle=True,
          verbose=1,
          validation_data=(np.array(X_valid), np.array(Y_valid)),
          class_weight={0:1,1:0.2}
          )


print("Finish fitting model")

# Make predictions
predictions_valid = model.predict(np.array(X_valid), batch_size=batch_size, verbose=1)




