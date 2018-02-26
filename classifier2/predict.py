import tensorflow as tf
slim = tf.contrib.slim
from PIL import Image
from inception_resnet_v2 import *
import numpy as np

import os

log_dir = './log/'
checkpoint_file = tf.train.latest_checkpoint(log_dir)
 
dir_path = 'data/alldata/False'
sample_images = os.listdir(dir_path)
num_classes = 2
failed = 0


sess = tf.Session()

input_tensor = tf.placeholder(tf.float32, shape=(None,299,299,3), name='input_image')
with slim.arg_scope(inception_resnet_v2_arg_scope()):
    logits, end_points = inception_resnet_v2(input_tensor, num_classes = num_classes, is_training=False)

saver = tf.train.Saver()
saver.restore(sess, checkpoint_file)

for image in sample_images:
    im = Image.open(os.path.join(dir_path, image)).resize((299,299))
    im = np.array(im)
    im = 2*(im/255.0)-1.0
    im = im.reshape(-1,299,299,3)
    p, _ = sess.run([end_points['Predictions'], logits], feed_dict={input_tensor: im})
    
    print p
    
    if np.argmax(p) == 1:
	failed = failed + 1
	img = Image.open(os.path.join(dir_path, image))
	img.show() 
	print image, classes[0][0]
    else:
	print image

print "%s failed of %s. %s percent acc" % (failed, len(sample_images), round(((1-(float(failed)/len(sample_images)))*100), 3) )

    
sess.close()
