import sys
sys.path.append('util')

import os
import argparse
from random import *
import shutil
from cred import *
import psycopg2
from db import *

outdir = './data/train_segmentation'
indir = './data/tiles'
maskin = './data/segmentation'

for dirp in ['train', 'test']:
	for cat in ['tiles', 'masks']:
		if os.path.exists(os.path.join(outdir, dirp, cat)): shutil.rmtree(os.path.join(outdir, dirp, cat))
		path = os.path.join(outdir, dirp, cat)
		if not os.path.exists(path): os.makedirs(path)

cur.execute('select x,y from segmentation_training_tiles where verified=true;')
tiles = cur.fetchall()
for tile in tiles:
	(x, y) = tile;
	dirp = 'test' if random() < 0.2 else 'train'
	
	img = '%s_%s.jpg' % (x, y)
	imgpath = os.path.join(indir, img)
	nimgpath = os.path.join(outdir, dirp, 'tiles', img)
	if os.path.exists(imgpath):
		shutil.copy(imgpath, nimgpath)

	imgpath = os.path.join(maskin, img)
	nimgpath = os.path.join(outdir, dirp, 'masks', img)
	if os.path.exists(imgpath):
		shutil.copy(imgpath, nimgpath)