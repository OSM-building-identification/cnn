''' 
Returns:
            tuple: Both training and test sets are returned.
'''
from PIL import Image
import numpy as np
import os
from keras.preprocessing import image


def load_data():


	img_width, img_height = 224, 224

	cwd = os.path.dirname(__file__) 

	train_path = cwd + "/data/train"
	groups = os.listdir(train_path)

	 

	Xlist, ylist = [], []
	for group in groups:

		p = train_path + "/" + group
		images = os.listdir(p)
		for imgPath in images:
			# print(dir_path+ "/" +imgPath)
			img = image.load_img(p+ "/" +imgPath, target_size=(img_width, img_height))
			x = image.img_to_array(img)
			x = np.expand_dims(x, axis=0)

			x = x * (1./255)

			Xlist.append(x)
			if group == 'False':
				ylist.append(0)
			else:
				ylist.append(1)

	
	X_train = np.vstack(Xlist)

	y_train = np.vstack(ylist)      

	#Testing path   	

	dir_path_test = cwd + "/data/test/False"  #False positive 98% accuracy 
	images = os.listdir(dir_path_test)


	X_test, y_test = [], []
	 
	for imgPath in images:
		img = image.load_img(dir_path_test+ "/" +imgPath, target_size=(img_width, img_height))
		x = image.img_to_array(img)
		# x = np.expand_dims(x, axis=0)

		x = x * (1./255)
		X_test.append(x)
		y_test.append(0)

	y_train = y_train.reshape(-1, 1)
	# X_test = np.array(X_test) 
	y_test = np.array(y_test).reshape(-1, 1)		

	print(np.shape(X_train))
	print(np.shape(y_train))
	print(np.shape(X_test))
	print(np.shape(y_test))
	return (X_train, y_train), (X_test, y_test)	

	


 

 