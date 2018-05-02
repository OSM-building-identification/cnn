# ------------------------------------------------------------------
#	Apply offset corrections and save tiles and masks ready for training
# ------------------------------------------------------------------
import sys
sys.path.append('util')

import os
import shutil
import tileMath
from PIL import Image
from PIL import ImageDraw
from db import *

outdir = './data/train_segmentation'
indir = './data/tiles'
maskin = './data/masks'

zoomlevel = 17
resolution = 256

# setup the output file structure if not already there
for cat in ['tiles', 'masks']:
	if os.path.exists(os.path.join(outdir, cat)): shutil.rmtree(os.path.join(outdir, cat))
	path = os.path.join(outdir, cat)
	if not os.path.exists(path): os.makedirs(path)

# select all segmentation_training_tiles that have been manually verified, and corrected
cur.execute('select x,y,dx,dy from segmentation_training_tiles where useable=true;')
tiles = cur.fetchall()
for tile in tiles:
	# redraw the mask, but with our offset
	(x, y, dx, dy) = tile;
	(left,top) = tileMath.tile2deg(x, y, zoomlevel)
	(right,bottom) = tileMath.tile2deg(x+1, y+1, zoomlevel)
	buildings = queryosm("SELECT ST_AsGeoJSON(geometry) FROM building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326)" % (right, bottom, left, top))
	xLength = abs(left-right)
	yLength = abs(top-bottom)
	
	img = Image.new("RGB", (resolution,resolution), (0,0,0))
	drw = ImageDraw.Draw(img, "RGB")
	
	for rawbuilding in buildings:
		building = json.loads(rawbuilding[0])
		try:	 
			buildingCoord = [(((buildingX-left)/xLength*resolution)+(dx/2),((top-buildingY)/yLength*resolution)+(dy/2)) for (buildingX,buildingY) in building["coordinates"][0]]
			drw.polygon(buildingCoord, fill=(255,255,255))
		except ValueError:
			print ("draw err")

	# save the corrected mask
	nimgpath = os.path.join(outdir, 'masks', '%s_%s.jpg' % (x, y))
	img.save(nimgpath)

	# save the tile
	img = '%s_%s.jpg' % (x, y)
	imgpath = os.path.join(indir, img)
	nimgpath = os.path.join(outdir, 'tiles', img)
	if os.path.exists(imgpath):
		shutil.copy(imgpath, nimgpath)