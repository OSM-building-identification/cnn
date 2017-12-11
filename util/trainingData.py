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
parser.add_argument("y", help = "Top Latitude", type = float)
parser.add_argument("x2", help = "Right Longitude", type = float)
parser.add_argument("y2", help = "Bottom Latitude", type = float)
args = parser.parse_args()

zoomlevel = 17

topLeft = [args.x, args.y]
bottomRight = [args.x2,args.y2]

def fresh(x,y):
	tilescur.execute('select 1 from training_tiles where x=%s and y=%s;', (x, y))
	return tilescur.fetchone() == None;

(startX, startY) = naip.deg2tile(topLeft[0],topLeft[1],zoomlevel)
(endX, endY) = naip.deg2tile(bottomRight[0],bottomRight[1],zoomlevel)

series = [(x, y) for x in range(startX, endX) for y in range(startY, endY)] 
random.shuffle(series)

truecount = 0
falsecount = 0

print len(series)

for (x,y) in series:
	if fresh(x, y):
		(left,top) = naip.tile2deg(x, y, zoomlevel)
		(right,bottom) = naip.tile2deg(x+1, y+1, zoomlevel)
		cur.execute("select exists(select 1 from building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326))",(right, bottom, left, top))
		(building, ) = cur.fetchone();
		if ((building == True and truecount <= falsecount/2) or (building == False and falsecount/2 <= truecount)):
			print (x, y, building, truecount, falsecount)
			if building == True:
				truecount = truecount+1
			else:
				falsecount = falsecount+1
			series.pop(0)

			img = naip.fetchTile(x,y,zoomlevel)
			if(img != None):
				file = open("%s/%s_%s.jpg" % (root,x, y), 'w')
				file.write(img)
				tilescur.execute("insert into training_tiles (x, y, has_building, verified ) values (%s, %s, %s, %s)",(x, y, building, building))
				tilesconn.commit()
		else:
			series.pop(0)
			series.append((x,y))
			print len(series)


	# print (x, y)
	# yrange = filter(lambda y: fresh(x, y), range(startY, endY))
	# urls = map(lambda y: naip.getUrl(x,y,zoomlevel), yrange)
	# rs = (grequests.get(u) for u in urls)
	# reses = grequests.map(rs, stream=True, size=10)
	# for index, res in enumerate(reses):
	# 	if res != None:
	# 		y = yrange[index]
	# 		print (x, y)
	# 		(left,top) = naip.tile2deg(x, y, zoomlevel)
	# 		(right,bottom) = naip.tile2deg(x+1, y+1, zoomlevel)
	# 		cur.execute("select exists(select 1 from building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326))",(right, bottom, left, top))
	# 		(building, ) = cur.fetchone();
	# 		tilescur.execute("insert into training_tiles (x, y, has_building, verified ) values (%s, %s, %s, %s)",(x, y, building, building))
	# 		file = open("%s/%s_%s.jpg" % (root,x, y), 'w')
	# 		shutil.copyfileobj(res.raw, file)    
	# 		tilesconn.commit()

tilesconn.close() 
conn.close() 
