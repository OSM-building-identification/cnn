import os
import naip
import argparse
import psycopg2
import grequests
import shutil
import random

from cred import *

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
parser.add_argument("y2", help = "Bottom Latitude", type = float)
parser.add_argument("x2", help = "Right Longitude", type = float)
parser.add_argument("y", help = "Top Latitude", type = float)
args = parser.parse_args()

zoomlevel = 17

topLeft = [args.x, args.y]
bottomRight = [args.x2,args.y2]

def fresh(x,y):
	tilescur.execute('select 1 from training_tiles where x=%s and y=%s;', (x, y))
	return tilescur.fetchone() == None;

def no_building(x,y):
	(left,top) = naip.tile2deg(x, y, zoomlevel)
	(right,bottom) = naip.tile2deg(x+1, y+1, zoomlevel)
	cur.execute("select exists(select 1 from building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326))",(right, bottom, left, top))
	(building, ) = cur.fetchone();
	return building == False

(startX, startY) = naip.deg2tile(topLeft[0],topLeft[1],zoomlevel)
(endX, endY) = naip.deg2tile(bottomRight[0],bottomRight[1],zoomlevel)

series = [(x, y) for x in range(startX, endX) for y in range(startY, endY)] 
random.shuffle(series)

truecount = 0
falsecount = 0

print len(series)

def save(li, building):
	for (x,y) in li:
		print (x,y,building)
		img = naip.fetchTile(x,y,zoomlevel)
		if(img != None):
			file = open("%s/%s_%s.jpg" % (root,x, y), 'w')
			file.write(img)
			tilescur.execute("insert into training_tiles (x, y, has_building, verified ) values (%s, %s, %s, %s)",(x, y, building, building))
			tilesconn.commit()

count=50

while True:
	has_none = []
	i = 0
	while len(has_none) < count and i <= len(series):
		(x, y) = series[i]
		if no_building(x,y) and fresh(x,y) :
			has_none.append((x,y))
		#print (x,y, no_building(x,y), fresh(x,y))
		i = i + 1
	save(has_none, False)

	if len(has_none) == 0:
		break;

	cur.execute("select ST_X(ST_centroid(geometry)), ST_Y(ST_centroid(geometry)) from building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326) order by random() limit %s;",(args.x2, args.y2, args.x, args.y, count))
	has_tiles = filter(lambda (x,y): fresh(x,y),list(set(map(lambda (x, y): naip.deg2tile(x,y,17), cur.fetchall()))))
	save(has_tiles, True)

	if len(has_tiles) == 0:
		break;

tilesconn.close() 
conn.close() 
