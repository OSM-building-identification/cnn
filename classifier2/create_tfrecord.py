import random
import tensorflow as tf
from dataset_utils import _dataset_exists, _get_filenames_and_classes, write_label_file, _convert_dataset


	
flags = tf.app.flags

flags.DEFINE_integer('seed', 0, 'seed')
flags.DEFINE_string('dir', None, 'inside cwd')
flags.DEFINE_float('split', 0.1, 'training/testing proportion')
flags.DEFINE_integer('nshards', 2, '# shards to split')
flags.DEFINE_string('filename', None, 'tfrecord filename header')
FLAGS = flags.FLAGS

def convert():

    if not FLAGS.filename:
        raise ValueError('need tfrecord filename arg!')
    if not FLAGS.dir:
        raise ValueError('need dataset directory arg!')
    if _dataset_exists(dataset_dir = FLAGS.dir, _NUM_SHARDS = FLAGS.nshards, output_filename = FLAGS.filename):
        print 'Dataset files already exist'
        return None


    images, classes = _get_filenames_and_classes(FLAGS.dir)
    ids = dict(zip(classes, range(len(classes))))
    barrier = int(FLAGS.split * len(images))
 
    random.seed(FLAGS.seed)
    random.shuffle(images)
    train = images[barrier:]
    validation = images[:barrier]

    
    _convert_dataset('train', train, ids, dataset_dir = FLAGS.dir, tfrecord_filename = FLAGS.filename, _NUM_SHARDS = FLAGS.nshards)
    _convert_dataset('validation', validation, ids, dataset_dir = FLAGS.dir, tfrecord_filename = FLAGS.filename, _NUM_SHARDS = FLAGS.nshards)


    labels = dict(zip(range(len(classes)), classes))
    write_label_file(labels, FLAGS.dir)
    print 'Finished converting the dataset!'

convert()
