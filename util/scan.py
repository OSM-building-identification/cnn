import sys
sys.path.append('./classifier/')

import os
import naip
import argparse
import psycopg2
import grequests
import shutil
import random
import time
from PIL import Image
from keras.preprocessing import image
from cStringIO import StringIO
import numpy as np

from cred import *

import cnn
cnn.model.load_weights('./best.h5')

root = "/home/ubuntu/tiles/"

conn = psycopg2.connect(
	database="osm",
	user = CRED['osm']['user'],
	password = CRED['osm']['pass'],
	host = CRED['osm']['host']
)
cur = conn.cursor()

tilesconn = psycopg2.connect(
	database="cucapstone",
	user = "cucapstone",
	password = CRED['db']['pass'],
	host = CRED['db']['host']
)
tilescur = tilesconn.cursor()

parser = argparse.ArgumentParser(description='Input longitude and lattitude')
parser.add_argument("x", help = "Left Longitude", type = float)
parser.add_argument("y", help = "Top Latitude", type = float)
args = parser.parse_args()

zoomlevel = 17

been_scanned = []
to_scan = []

def is_scannable(x,y):
	if str(x)+str(y) in been_scanned:
		return False

	(left,top) = naip.tile2deg(x, y, zoomlevel)
	(right,bottom) = naip.tile2deg(x+1, y+1, zoomlevel)
	cur.execute("select exists(select 1 from building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326))",(right, bottom, left, top))
	(building, ) = cur.fetchone();
	if building == True:
		return False

	tilescur.execute("select exists(select 1 from predictions where x=%s and y=%s)",(x,y))
	(scanned, ) = tilescur.fetchone();

	return scanned == False

def findScannable(x,y):
	dirs = [(0,1),(0,-1),(1,0),(-1,0)]
	(dx, dy) = random.choice(dirs)
	print ('moving', dx, dy)
	while(True):
		if(is_scannable(x,y)):
			return (x,y)
		x = x+dx
		y = y+dy

def findNeighbors(x,y):
	dirs = [(-1,1), (-1,-1), (0, 1), (0,-1), (1,1), (1,-1), (1, 0), (-1,0)]
	coords = map(lambda (dx,dy): (x+dx, y+dy), dirs)
	return filter(lambda (x,y): is_scannable(x,y), coords)[:2]

def scan(x, y):
	img = naip.fetchTile(x,y,zoomlevel)
	if img != None:
		file_jpgdata = StringIO(img)
		i = Image.open(file_jpgdata)
		i = i.resize((cnn.img_width, cnn.img_height))
		arr = image.img_to_array(i)
		arr = np.expand_dims(arr, axis=0)
		arr = arr * (1./255)

		imgs = np.vstack([arr])
		classes = cnn.model.predict_classes(imgs, batch_size=10, verbose=0)
		building = 'true' if classes[0][0] == 1 else 'false'
		tilescur.execute("insert into predictions (x, y, has_building) values (%s, %s, %s)",(x, y, building))
		tilesconn.commit()
		print ('scanned', x, y, building)
		been_scanned.append(str(x)+str(y))

(x, y) = naip.deg2tile(args.x,args.y,zoomlevel)


while(True):
	if len(to_scan) == 0:
		to_scan.append(findScannable(x,y))
	else:
		new_to_scan = []
		print to_scan
		for (x,y) in to_scan:
			scan(x,y)
			neighbors = findNeighbors(x,y)
			new_to_scan = new_to_scan + neighbors
		to_scan = list(set(new_to_scan))


tilesconn.close() 
conn.close() 
