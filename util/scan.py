import sys
sys.path.append('./classifier/')

from geojson import GeometryCollection, Polygon
import os
import math
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
from db import *

import cnn
cnn.model.load_weights('./best.h5')

root = "./data/tiles/"
zoomlevel = 17

parser = argparse.ArgumentParser(description='Input longitude and lattitude')
parser.add_argument("x", help = "Left Longitude", type = float)
parser.add_argument("y2", help = "Bottom Latitude", type = float)
parser.add_argument("x2", help = "Right Longitude", type = float)
parser.add_argument("y", help = "Top Latitude", type = float)
args = parser.parse_args()

topLeft = [args.x, args.y]
bottomRight = [args.x2,args.y2]

(startX, startY) = naip.deg2tile(topLeft[0],topLeft[1],zoomlevel)
(endX, endY) = naip.deg2tile(bottomRight[0],bottomRight[1],zoomlevel)
startbox = (startX, startY, endX, endY)

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

def getArea(bbox):
	(startX, startY, endX, endY) = bbox
	dx = endX-startX
	dy = endY-startY
	return dx*dy 

def hasData(bbox):
	(startX, startY, endX, endY) = bbox

	(left,top) = naip.tile2deg(startX, startY, zoomlevel)
	(right,bottom) = naip.tile2deg(endX, endY, zoomlevel)
	building = queryosm("select exists(select 1 from building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326))" % (right, bottom, left, top))[0][0]
	if building == True:
		return True
	cur.execute("select exists(select 1 from predictions where x>=%s and y>=%s and x<%s and y<%s and has_building=TRUE)",(startX, startY, endX, endY))
	(scanned, ) = cur.fetchone();
	return scanned

def getPolygon(bbox):
	(startX, startY, endX, endY) = bbox
	(left,top) = naip.tile2deg(startX, startY, zoomlevel)
	(right,bottom) = naip.tile2deg(endX, endY, zoomlevel)
	return Polygon([[
		(left, top), 
		(left, bottom),
		(right, bottom),
		(right, top),
		(left, top)
	]])

def scan(x, y):
	if hasData((x, y, x+1, y+1)):
		return
	img = naip.fetchTile(x,y,zoomlevel)
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

quads = [startbox]

def isInside(point, bbox):
	(startX, startY, endX, endY) = bbox
	(x, y) = point
	return ((x >= startX and x <= endX) and (y >= startY and y <= endY))

def intersects(bbox, obbox):
	(startX, startY, endX, endY) = bbox
	(ostartX, ostartY, oendX, oendY) = obbox
	return  isInside((ostartX, ostartY), bbox) or isInside((oendX, oendY), bbox) or isInside((startX, startY), obbox) or isInside((endX, endY), obbox)

def getNeighbors(bbox):
	global quads
	(startX, startY, endX, endY) = bbox
	dx = endX-startX
	dy = endY-startY
	def fi(bbox):
		return not hasData(bbox) and all(not intersects(bbox, quad) for quad in quads)
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

#scanned = []
skipped = []
while len(quads) > 0:
	print len(quads)
	quad = quads.pop(-1)
	if getArea(quad) < 20:
		print ('scan', quad, getArea(quad))
		scanAll(quad)
		#scanned.append(getPolygon(quad))
	elif hasData(quad):
		quads.extend(getQuads(quad))
	else:
		#print ('skipping', quad)
		skipped.append(getPolygon(quad))

print GeometryCollection(skipped)

conn.close() 
