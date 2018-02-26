import tensorflow as tf
import os
import sys
import tarfile 
from six.moves import urllib

url = "http://download.tensorflow.org/models/inception_resnet_v2_2016_08_30.tar.gz"
checkpoints_dir = './ckpt'

def download_and_uncompress_tarball(tarball_url, dataset_dir):
  
    f = tarball_url.split('/')[-1]
    path = os.path.join(dataset_dir, f)

    def progress(count, block_size, total_size):
        sys.stdout.write('\r>> Downloading %s %.1f%%' % (f, float(count * block_size) / float(total_size) * 100))
        sys.stdout.flush()

    path, _ = urllib.request.urlretrieve(tarball_url, path, progress)     
    print('Downloaded', f)
    tarfile.open(path, 'r:gz').extractall(dataset_dir)


if not tf.gfile.Exists(checkpoints_dir):
    tf.gfile.MakeDirs(checkpoints_dir)
    download_and_uncompress_tarball(url, checkpoints_dir)
print 'Extracted checkpoint file'
