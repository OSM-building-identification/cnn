# -------------------------------------------
# Fetches training data for image segmentation
# -------------------------------------------
import sys
sys.path.append('util')

from PIL import Image
from PIL import ImageDraw
from cStringIO import StringIO
import json
import argparse
import os

import imagery
import tileMath
from db import *

# create output directories for images
maskDir = "./data/masks/"
if not os.path.exists(maskDir): os.makedirs(maskDir)

tileDir = "./data/tiles/"
if not os.path.exists(tileDir): os.makedirs(tileDir)

parser = argparse.ArgumentParser(description='Input longitude and lattitude')
parser.add_argument("x", help = "Left Longitude", type = float)
parser.add_argument("y2", help = "Bottom Latitude", type = float)
parser.add_argument("x2", help = "Right Longitude", type = float)
parser.add_argument("y", help = "Top Latitude", type = float)
args = parser.parse_args()

zoomlevel = 17

# given an x,y,z tile coordinate draw a "ground truth" mask using osm contour data
def getMask(startX,startY, zoomlevel):
	# skip if this is already in our tarining data
	cur.execute('select * from segmentation_training_tiles where x=%d and y=%d' % (startX, startY))
	res = cur.fetchone()
	if res != None:
		print 'skip'
		return

	# find the lat lng bounding box of the tile
	endX = startX+1
	endY = startY+1
	(left,top) = tileMath.tile2deg(startX, startY, zoomlevel)
	(right,bottom) = tileMath.tile2deg(endX, endY, zoomlevel)
	
	# find all buildings in this tile
	buildings = queryosm("SELECT ST_AsGeoJSON(geometry) FROM building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326)" % (right, bottom, left, top))
	
	# size in degrees of each side of the tile. x and y may not be the same
	xLength = abs(left-right)
	yLength = abs(top-bottom)
	
	# create a new image to draw our mask on with a black (0,0,0) background
	img = Image.new("RGB", (256,256), (0,0,0))
	drw = ImageDraw.Draw(img, "RGB")
	
	# for each building vertex, convert its points to 0-255 coordinates on the image
	# and draw them as a white poly
	for rawbuilding in buildings:
		building = json.loads(rawbuilding[0])
		try:	 
			buildingCoord = [((buildingX-left)/xLength*255,(top-buildingY)/yLength*255) for (buildingX,buildingY) in building["coordinates"][0]]
			drw.polygon(buildingCoord, fill=(255,255,255))
		except ValueError:
			print ("could not fetch", startX, startY)

	# save the output to our masks directory, and download the tile from naip
	img.save("%s/%s_%s.jpg" % (maskDir,startX,startY))
	try:
		realImg = imagery.fetchTile(startX,startY,zoomlevel)
		file_jpgdata = StringIO(realImg)
		i = Image.open(file_jpgdata).convert('RGB')
		i.save("%s/%s_%s.jpg" % (tileDir,startX,startY))
	except TypeError:
		print ("failed to load tile", startX, startY)

	# mark it as saved in segmentation_training_tiles, but not verified
	cur.execute("insert into segmentation_training_tiles (x, y, verified ) values (%s, %s, %s)",(startX, startY, False))
	conn.commit()

	print(startX, startY)



(startX, startY) = tileMath.deg2tile(args.x,args.y,zoomlevel)
(endX, endY) = tileMath.deg2tile(args.x2,args.y2,zoomlevel)
startbox = (startX, startY, endX, endY)

# for ever and ever, randomly sample an OSM building and get its mask and tile.
while True:
	count = 50
	res = queryosm("select ST_X(ST_centroid(geometry)), ST_Y(ST_centroid(geometry)) from building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326) order by random() limit %s;" % (args.x2, args.y2, args.x, args.y, count))
	tiles = list(set(map(lambda coord: tileMath.deg2tile(coord[0],coord[1],zoomlevel), res)))
	print len(tiles)
	for x,y in tiles:
		getMask(x,y,zoomlevel)
