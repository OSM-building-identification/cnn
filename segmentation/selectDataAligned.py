import sys
sys.path.append('util')

import os
import argparse
from random import *
import shutil
from cred import *
import psycopg2
import naip
from PIL import Image
from PIL import ImageDraw
from db import *

outdir = './data/hires-train_segmentation'
indir = './data/hires-tiles'
maskin = './data/hires-segmentation'

zoomlevel = 19
resolution = 512

for cat in ['tiles', 'masks']:
	if os.path.exists(os.path.join(outdir, cat)): shutil.rmtree(os.path.join(outdir, cat))
	path = os.path.join(outdir, cat)
	if not os.path.exists(path): os.makedirs(path)

cur.execute('select x,y,dx,dy from segmentation_training_tiles where useable=true;')
tiles = cur.fetchall()
for tile in tiles:
	(x, y, dx, dy) = tile;
	(left,top) = naip.tile2deg(x, y, zoomlevel)
	(right,bottom) = naip.tile2deg(x+1, y+1, zoomlevel)
	buildings = queryosm("SELECT ST_AsGeoJSON(geometry) FROM building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326)" % (right, bottom, left, top))
	xLength = abs(left-right)
	yLength = abs(top-bottom)
	
	img = Image.new("RGB", (resolution,resolution), (0,0,0))
	drw = ImageDraw.Draw(img, "RGB")
	
	for rawbuilding in buildings:
		building = json.loads(rawbuilding[0])
		try:	 
			buildingCoord = [(((buildingX-left)/xLength*resolution)+dx,((top-buildingY)/yLength*resolution)+dy) for (buildingX,buildingY) in building["coordinates"][0]]
			drw.polygon(buildingCoord, fill=(255,255,255))
		except ValueError:
			print ("could not fetch", startX, startY)

	# img.show()
	nimgpath = os.path.join(outdir, 'masks', '%s_%s.jpg' % (x, y))
	img.save(nimgpath)


	img = '%s_%s.jpg' % (x, y)
	imgpath = os.path.join(indir, img)
	nimgpath = os.path.join(outdir, 'tiles', img)
	if os.path.exists(imgpath):
		shutil.copy(imgpath, nimgpath)