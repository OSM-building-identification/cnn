import tensorflow as tf

#use current model
from inception_resnet_v2 import *

class modelTest(tf.test.TestCase):

    def testBuildLogits(self):
    	batch_size = 5
        height, width = 299, 299
        num_classes = 2
    	
	with self.test_session():

		inputs = tf.random_uniform((batch_size, height, width, 3))
		logits, _ = inception_resnet_v2(inputs, num_classes)
      
		self.assertTrue(logits.op.name.startswith('InceptionResnetV2/Logits'))
		self.assertListEqual(logits.get_shape().as_list(), [batch_size, num_classes])

    

if __name__ == '__main__':
    tf.test.main()
