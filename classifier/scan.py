# -------------------------------------
#	Classifier Scan for missing buildings
# -------------------------------------
import sys
sys.path.append('./util/')

import math
import argparse
from PIL import Image
from cStringIO import StringIO
import numpy as np
import ast

import tileMath
import imagery
from cred import *
from db import *

# take a bounding box and split it into 4 quadrants, returned as bounding boxes
def getQuads(bbox):
	(startX, startY, endX, endY) = bbox
	dx = endX-startX
	dy = endY-startY
	mx = startX + math.floor(dx/float(2))
	my = startY + math.floor(dy/float(2))
	return [
		(startX, startY, mx, my), #top left
		(mx, startY, endX, my), #top right
		(startX, my, mx, endY), #bottom left
		(mx, my, endX, endY) #bottom right
	]

# return the size of a bounding box in tiles
def getArea(bbox):
	(startX, startY, endX, endY) = bbox
	dx = endX-startX
	dy = endY-startY
	return dx*dy

# check to see if the bounding box already has OSM data in it.
# anyData param specifies if even "False" predictions should be taken into account
def hasData(bbox, anyData):
	(startX, startY, endX, endY) = bbox

	(left,top) = tileMath.tile2deg(startX, startY, zoomlevel)
	(right,bottom) = tileMath.tile2deg(endX, endY, zoomlevel)

	# if there is a building in OSM with the data already, just exit
	building = queryosm("select exists(select 1 from building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326))" % (right, bottom, left, top))[0][0]
	if building == True:
		return True

	# check to see if we've already predicted. if anyData is true, predicitions true or false count
	if anyData:
		cur.execute("select exists(select 1 from predictions where x>=%s and y>=%s and x<%s and y<%s)",(startX, startY, endX, endY))
	else:
		cur.execute("select exists(select 1 from predictions where x>=%s and y>=%s and x<%s and y<%s and has_building=TRUE)",(startX, startY, endX, endY))
	(scanned, ) = cur.fetchone();
	return scanned

# given a single tile, make a prediction, and save it in the db
def scan(x, y):
	if hasData((x, y, x+1, y+1), True):
		return
	img = imagery.fetchTile(x,y,zoomlevel)
	if img == None:
		print ('failed to fetch', x, y)
	if img != None:
		try:
			file_jpgdata = StringIO(img)
			i = Image.open(file_jpgdata)
		except IOError:
			return False

		i = i.resize((cnn.img_width, cnn.img_height))
		arr = image.img_to_array(i)
		arr = np.expand_dims(arr, axis=0)
		arr = arr * (1./255)

		imgs = np.vstack([arr])
		classes = cnn.model.predict_classes(imgs, batch_size=10, verbose=0)
		building = 'true' if classes[0][0] == 1 else 'false'
		cur.execute("insert into predictions (x, y, has_building) values (%s, %s, %s)",(x, y, building))
		conn.commit()
		print ('scanned', x, y, building)
		return classes[0][0] == 1


def isInside(point, bbox):
	(startX, startY, endX, endY) = bbox
	(x, y) = point
	return ((x >= startX and x <= endX) and (y >= startY and y <= endY))

def intersects(bbox, obbox):
	(startX, startY, endX, endY) = bbox
	(ostartX, ostartY, oendX, oendY) = obbox
	return  isInside((ostartX, ostartY), bbox) or isInside((oendX, oendY), bbox) or isInside((startX, startY), obbox) or isInside((endX, endY), obbox)

# in an infinite grid of bboxes all the size of this bbox, returns the 8 neighbors around bbox
def getNeighbors(bbox):
	global quads
	(startX, startY, endX, endY) = bbox
	dx = endX-startX
	dy = endY-startY
	def fi(bbox):
		return not hasData(bbox, False) and all(not intersects(bbox, quad) for quad in quads)
	return filter(fi, [
		(startX-dx, startY-dy, startX, startY), #tl
		(startX, startY-dy, endX, startY), #tm
		(endX, startY-dy, endX+dx, startY), #tr
		(endX, startY, endX+dx, endY), #r
		(endX, endY, endX+dx, endY+dy), #br
		(startX, endY, endX, endY+dy), #bm
		(startX-dx, endY, startX, endY+dy), #bl
		(startX-dx, startY, startX, endY) #l
	])

# scan all tiles within a quad. If it finds enough buildings:
# it adds its neighbors to the quads stack
def scanAll(quad):
	global quads
	(startX, startY, endX, endY) = quad
	total = (endX-startX)*(endY-startY)
	buildingCount = 0
	for x in range(int(startX), int(endX)):
		for y in range(int(startY), int(endY)):
			b = scan(x,y)
			if b:
				buildingCount = buildingCount+1
	if total > 0 and float(buildingCount)/total >= 0.25:
		ns = getNeighbors(quad)
		print ('adding neighbors', len(ns))
		quads = ns+quads

# given a list of roads returns all adjacent tiles
def getTilesNearRoads(roads):
	keys = range(len(roads))
	values = []
	roadTiles = {}
	neighbors = []
	tmp = []
	roadTilesLst = []
	for rawroad in roads:
		del tmp[:]
		x = ast.literal_eval(rawroad[0])
		coords = x.get('coordinates', "No coordinates found")

		# Convert to tile numbers to find neighbors
		for [x, y] in coords:
			tmp.append(tileMath.deg2tile(x, y, zoomlevel))
		values.append(tmp)
	# Need this to associate each LineString with the polygon that will be scanned
	for i in keys:
		roadTiles[i] = values[i]

	# Make large list of all road tiles
	for key, value in roadTiles.iteritems():
		for (x, y) in value:
			roadTilesLst.append((x, y))

	# Find all tiles surrounding roads and make larger list of neighbors
	for (x, y) in roadTilesLst:
		neighbors.append((x+1, y+1))
		neighbors.append((x-1, y-1))
		neighbors.append((x+1, y-1))
		neighbors.append((x-1, y+1))
		neighbors.append((x, y+1))
		neighbors.append((x, y-1))
		neighbors.append((x+1, y))
		neighbors.append((x-1, y))
	#print neighbors
	print len(set(neighbors))
	return list(set(neighbors))

# select roads from OSM db
def getRoads(bbox):
	(startX, startY, endX, endY) = bbox
	(left,top) = tileMath.tile2deg(startX, startY, zoomlevel)
	(right,bottom) = tileMath.tile2deg(endX, endY, zoomlevel)
	roads = queryosm("select ST_AsGeoJSON(geometry) from highway_line where highway='tertiary' and ST_Intersects(geometry, ST_MakeEnvelope(%s, %s, %s, %s, 4326))" % (right, bottom, left, top))
	return roads

# scan the area of a quad for all roads.
def scanRoads(quad):
	global quads
	roadsToScan = getRoads(quad)
	tilesToScan = getTilesNearRoads(roadsToScan)
	for (x,y) in tilesToScan:
		scan(x, y)

if __name__=="__main__":
	from keras.preprocessing import image
	import cnn

	cnn.model.load_weights('./data/weights/classifier.h5')

	root = "./data/tiles/"
	zoomlevel = 17

	parser = argparse.ArgumentParser(description='Input longitude and lattitude')
	parser.add_argument("type", help = "[quads|roads]", type = str)
	parser.add_argument("x", help = "Left Longitude", type = float)
	parser.add_argument("y2", help = "Bottom Latitude", type = float)
	parser.add_argument("x2", help = "Right Longitude", type = float)
	parser.add_argument("y", help = "Top Latitude", type = float)
	args = parser.parse_args()

	topLeft = [args.x, args.y]
	bottomRight = [args.x2,args.y2]

	(startX, startY) = tileMath.deg2tile(topLeft[0],topLeft[1],zoomlevel)
	(endX, endY) = tileMath.deg2tile(bottomRight[0],bottomRight[1],zoomlevel)
	startbox = (startX, startY, endX, endY)

	quads = [startbox]

	# depending on the type argument, scan with roads or by quadtree
	if args.type == 'roads':
		quad = quads.pop(-1)
		scanRoads(quad)
	if args.type == 'quads':
		while len(quads) > 0:
			print len(quads)
			quad = quads.pop(-1)
			if getArea(quad) < 20:
				print ('scan', quad, getArea(quad))
				scanAll(quad)
			elif hasData(quad, True):
				quads.extend(getQuads(quad))
			else:
				print ('skipping', quad)
	
	conn.close()
