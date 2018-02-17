import sys
sys.path.append('util')

import os
import argparse
from random import *
import shutil
from cred import *
import psycopg2
from db import *

outdir = './data/2class_train_segmentation'
indir = './data/tiles'
maskin = './data/building_masks'
egdemaskin = './data/edge_masks'

for cat in ['tiles', 'building_masks', 'edge_masks']:
	if os.path.exists(os.path.join(outdir, cat)): shutil.rmtree(os.path.join(outdir, cat))
	path = os.path.join(outdir, cat)
	if not os.path.exists(path): os.makedirs(path)

cur.execute('select x,y from segmentation_training_tiles where useable=true;')
tiles = cur.fetchall()
for tile in tiles:
	(x, y) = tile;
	
	img = '%s_%s.jpg' % (x, y)
	imgpath = os.path.join(indir, img)
	nimgpath = os.path.join(outdir, 'tiles', img)
	if os.path.exists(imgpath):
		shutil.copy(imgpath, nimgpath)

	imgpath = os.path.join(maskin, img)
	nimgpath = os.path.join(outdir, 'building_masks', img)
	if os.path.exists(imgpath):
		shutil.copy(imgpath, nimgpath)

	imgpath = os.path.join(egdemaskin, img)
	nimgpath = os.path.join(outdir, 'edge_masks', img)
	if os.path.exists(imgpath):
		shutil.copy(imgpath, nimgpath)