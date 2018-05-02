# -----------------------------------
#	Classifier Training Data Gathering
# -----------------------------------
import sys
sys.path.append('./util/')

import os
import imagery
import tileMath
import argparse
import random

from cred import *
from db import *

zoomlevel = 17

# Check to see if this tile is already in the training_tiles table
def fresh(x,y):
	cur.execute('select 1 from training_tiles where x=%s and y=%s;', (x, y))
	return cur.fetchone() == None;

# Check if there is no building in a tile according to OSM database
def no_building(x,y):
	(left,top) = tileMath.tile2deg(x, y, zoomlevel)
	(right,bottom) = tileMath.tile2deg(x+1, y+1, zoomlevel)
	res = queryosm("select exists(select 1 from building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326))" % (right, bottom, left, top))
	building = res[0][0]
	return building == False

if __name__=='__main__':
	# create the output directory if it doesn't already exist
	root = "./data/tiles/"
	if not os.path.exists(root): os.makedirs(root)

	parser = argparse.ArgumentParser(description='Input longitude and lattitude')
	parser.add_argument("x", help = "Left Longitude", type = float)
	parser.add_argument("y2", help = "Bottom Latitude", type = float)
	parser.add_argument("x2", help = "Right Longitude", type = float)
	parser.add_argument("y", help = "Top Latitude", type = float)
	args = parser.parse_args()

	topLeft = [args.x, args.y]
	bottomRight = [args.x2,args.y2]

	(startX, startY) = tileMath.deg2tile(topLeft[0],topLeft[1],zoomlevel)
	(endX, endY) = tileMath.deg2tile(bottomRight[0],bottomRight[1],zoomlevel)
	
	# flatten the bounding box and randomly sample tiles from it
	series = [(x, y) for x in range(startX, endX) for y in range(startY, endY)] 
	random.shuffle(series)

	truecount = 0
	falsecount = 0

	print len(series)

	# save a list of (x,y) tiles with bool "building" into training_tiles table
	def save(li, building):
		for (x,y) in li:
			print (x,y,building)
			img = imagery.fetchTile(x,y,zoomlevel)
			if(img != None):
				file = open("%s/%s_%s.jpg" % (root,x, y), 'w')
				file.write(img)
				cur.execute("insert into training_tiles (x, y, has_building, verified ) values (%s, %s, %s, %s)",(x, y, building, building))
				conn.commit()

	count=5

	# continually randomly sample tiles. if there are too many of one category,
	# we find the other category explicitly from OSM
	while True:
		has_none = []
		i = 0
		while len(has_none) < count and i < len(series):
			(x, y) = series[i]
			if no_building(x,y) and fresh(x,y) :
				has_none.append((x,y))
			i = i + 1
		save(has_none, False)

		if len(has_none) == 0:
			break;

		res = queryosm("select ST_X(ST_centroid(geometry)), ST_Y(ST_centroid(geometry)) from building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326) order by random() limit %s;" % (args.x2, args.y2, args.x, args.y, count))
		has_tiles = filter(lambda coord: fresh(coord[0],coord[1]),list(set(map(lambda coord: tileMath.deg2tile(coord[0],coord[1],17), res))))
		save(has_tiles, True)

		if len(has_tiles) == 0:
			break;
