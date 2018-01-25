import os
import argparse
from random import *
import shutil
from cred import *
import psycopg2
from db import *

outdir = './data'
indir = './data/tiles'

for dirp in ['train', 'test']:
	for cat in ['true', 'false']:
		shutil.rmtree(os.path.join(outdir, dirp, cat))
		path = os.path.join(outdir, dirp, cat)
		if not os.path.exists(path): os.makedirs(path)

cur.execute('select x,y,has_building from training_tiles where verified=true;')
tiles = cur.fetchall()
for tile in tiles:
	(x, y, building) = tile;
	dirp = 'test' if random() < 0.2 else 'train'
	cat = 'true' if building else 'false'
	img = '%s_%s.jpg' % (x, y)
	imgpath = os.path.join(indir, img)
	nimgpath = os.path.join(outdir, dirp, cat, img)
	print (imgpath, nimgpath, dirp, cat, x, y)
	
	if os.path.exists(imgpath):
		shutil.copy(imgpath, nimgpath)
