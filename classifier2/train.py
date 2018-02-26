import os
import sys 
import tensorflow as tf
import inception_preprocessing
  
from inception_resnet_v2 import inception_resnet_v2, inception_resnet_v2_arg_scope
from tensorflow.contrib import slim
from tensorflow.contrib.framework.python.ops.variables import get_or_create_global_step
from tensorflow.python.platform import tf_logging as logging

import time


# Dataset Info
dataset_dir = './data/'
log_dir = './log'
checkpoint_file = './ckpt/inception_resnet_v2_2016_08_30.ckpt'
image_size = 299
num_classes = 2

labels_file = './data/labels.txt'
labels = open(labels_file, 'r') 

 
labels_to_name = {}
for line in labels:
    label, string_name = line.split(':')
    string_name = string_name[:-1] 	
    labels_to_name[int(label)] = string_name
    
file_pattern = 'data_%s_*.tfrecord'		 

items_to_descriptions = {
    'image': 'A 3-channel RGB coloured aerial image that either has buildings or does not have buildings',
    'label': '0:False, 1:True'
}


# Training Info 
num_epochs = 20
batch_size = 32
initial_learning_rate = 0.0002
decay_factor = 0.7
num_epochs_before_decay = 2

def get_split(split_name, dataset_dir, file_pattern=file_pattern, prefix='data'):
    
    if split_name not in ['train', 'validation']:
        raise ValueError('split_name %s must be train or validation' % (split_name))


    file_pattern_path = os.path.join(dataset_dir, file_pattern % (split_name))	
    
    #make sure all images are converted to tfrecord format
    num_samples = 0
    prefix = prefix + '_' + split_name
    total = [os.path.join(dataset_dir, file) for file in os.listdir(dataset_dir) if file.startswith(prefix)]

    for tfrecord_file in total:
        for each in tf.python_io.tf_record_iterator(tfrecord_file):
            num_samples += 1
    print "Number of samples: %d" % (num_samples)

    #Reader and decoding things
    reader = tf.TFRecordReader

    keys_to_features = {
      'image/encoded': tf.FixedLenFeature((), tf.string, default_value=''),
      'image/format': tf.FixedLenFeature((), tf.string, default_value='jpg'),
      'image/class/label': tf.FixedLenFeature(
          [], tf.int64, default_value=tf.zeros([], dtype=tf.int64)),
    }

    items_to_handlers = {
    'image': slim.tfexample_decoder.Image(),
    'label': slim.tfexample_decoder.Tensor('image/class/label'),
    }

    decoder = slim.tfexample_decoder.TFExampleDecoder(keys_to_features, items_to_handlers)
    labels_to_name_dict = labels_to_name

    dataset = slim.dataset.Dataset(
        data_sources = file_pattern_path,
        decoder = decoder,
        reader = reader,
        num_readers = 4,
        num_samples = num_samples,
        num_classes = num_classes,
        labels_to_name = labels_to_name_dict,
        items_to_descriptions = items_to_descriptions)

    return dataset


def load_batch(dataset, batch_size=16, height=299, width=299, is_training=False):
    
    data_provider = slim.dataset_data_provider.DatasetDataProvider(
        dataset, common_queue_capacity=32,
        common_queue_min=8)
    image_raw, label = data_provider.get(['image', 'label'])
    
    # Preprocess image by Inception
    image = inception_preprocessing.preprocess_image(image_raw, height, width, is_training=is_training)
    
    
    image_raw = tf.expand_dims(image_raw, 0)
    image_raw = tf.image.resize_images(image_raw, [height, width])
    image_raw = tf.squeeze(image_raw)

    # Batch it up
    images, images_raw, labels = tf.train.batch(
          [image, image_raw, label],
          batch_size=batch_size,
          num_threads=4,
          capacity=4 * batch_size, 
	  allow_smaller_final_batch = True)
    
    return images, images_raw, labels


def run():
    if not os.path.exists(log_dir):
	os.mkdir(log_dir)

    with tf.Graph().as_default() as graph:
        tf.logging.set_verbosity(tf.logging.INFO)

        dataset = get_split('train', dataset_dir, file_pattern=file_pattern)
        images, _, labels = load_batch(dataset, batch_size=batch_size)

        num_batches_per_epoch = int(dataset.num_samples / batch_size)
        num_steps_per_epoch = num_batches_per_epoch #1 step = 1 batch processed
        
	
	decay_steps = int(num_epochs_before_decay * num_steps_per_epoch) 

        #Model inference
        with slim.arg_scope(inception_resnet_v2_arg_scope()):
            logits, end_points = inception_resnet_v2(images, num_classes = dataset.num_classes, is_training = True)
        exclude = ['InceptionResnetV2/Logits', 'InceptionResnetV2/AuxLogits']
        variables_to_restore = slim.get_variables_to_restore(exclude = exclude)

        one_hot_labels = slim.one_hot_encoding(labels, dataset.num_classes)

        #Performs the equivalent to tf.nn.sparse_softmax_cross_entropy_with_logits but enhanced with checks
        loss = tf.losses.softmax_cross_entropy(onehot_labels = one_hot_labels, logits = logits)
        total_loss = tf.losses.get_total_loss()    #regularization losses

        global_step = tf.train.get_or_create_global_step()

	#exponentially decaying learning rate after every 2 epochs
        lr = tf.train.exponential_decay(
            learning_rate = initial_learning_rate,
            global_step = global_step,
            decay_steps = decay_steps,
            decay_rate = decay_factor,
            staircase = True)

        optimizer = tf.train.AdamOptimizer(learning_rate = lr)

        train_op = slim.learning.create_train_op(total_loss, optimizer)

        #Stated metrics from predictions
        predictions = tf.argmax(end_points['Predictions'], 1)
        probabilities = end_points['Predictions']
        accuracy, accuracy_update = tf.metrics.accuracy(predictions, labels)
        metrics_op = tf.group(accuracy_update, probabilities)

        tf.summary.scalar('losses/Total_Loss', total_loss)
        tf.summary.scalar('accuracy', accuracy)
        tf.summary.scalar('learning_rate', lr)
        my_summary_op = tf.summary.merge_all()

	
	#logging on time elapsed for each global step
        def train_step(sess, train_op, global_step):
            
            start_time = time.time()
            total_loss, step, _ = sess.run([train_op, global_step, metrics_op])
            
	    t = time.time() - start_time

            logging.info('global step %s: loss: %.4f (%.1f sec/step)', step, total_loss, t)
            return total_loss, step

        #restores variables from a checkpoint 
        saver = tf.train.Saver(variables_to_restore)
	def restore_fn(sess):
            return saver.restore(sess, checkpoint_file)

        #summary_op causes crash?
	sv = tf.train.Supervisor(logdir = log_dir, summary_op = None, init_fn = restore_fn)



	#managed_session to check if things are going fine
        with sv.managed_session() as sess:

            for step in xrange(num_steps_per_epoch * num_epochs):	 
                if step % num_batches_per_epoch == 0:	 		
                    logging.info('Epoch %s/%s', step/num_batches_per_epoch + 1, num_epochs)
                    lr, accuracy = sess.run([lr, accuracy])
                    logging.info('Current Learning Rate: %s', lr)
                    logging.info('Current Streaming Accuracy: %s', accuracy)


                    logits, probs, predictions, labels = sess.run([logits, probabilities, predictions, labels])
                    print 'logits: \n', logits
                    print 'Probabilities: \n', probs
                    print 'predictions: \n', predictions 
                    print 'Labels:\n:', labels

                if step % 10 == 0:
                    loss, _ = train_step(sess, train_op, sv.global_step)
                    summaries = sess.run(my_summary_op)
                    sv.summary_computed(sess, summaries)
                else:
                    loss, _ = train_step(sess, train_op, sv.global_step)

            logging.info('Finished training!.') 
            logging.info('Final Loss: %s', loss)
            logging.info('Final Accuracy: %s', sess.run(accuracy))


            # saver.save(sess, "./data_model.ckpt")
            sv.saver.save(sess, sv.save_path, global_step = sv.global_step)


run()
































