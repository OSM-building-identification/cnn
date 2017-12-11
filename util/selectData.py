import os
import argparse
from random import *
import shutil
from cred import *
import psycopg2

conn = psycopg2.connect(
	database="cucapstone",
	user = "cucapstone",
	password = CRED['db']['pass'],
	host = CRED['db']['host']
)
cur = conn.cursor()

outdir = './data'
indir = '../tiles'

shutil.rmtree(outdir)
for dirp in ['train', 'test']:
	for cat in ['true', 'false']:
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
	
	shutil.copy(imgpath, nimgpath)
