import os
import naip
import argparse
import psycopg2
import grequests
import shutil

conn = psycopg2.connect("dbname=osm user=satchel")
cur = conn.cursor()

parser = argparse.ArgumentParser(description='Input longitude and lattitude')
parser.add_argument("x", help = "Left Longitude", type = float)
parser.add_argument("y", help = "Top Latitude", type = float)
parser.add_argument("x2", help = "Right Longitude", type = float)
parser.add_argument("y2", help = "Bottom Latitude", type = float)
args = parser.parse_args()

zoomlevel = 17

topLeft = [args.x, args.y]
bottomRight = [args.x2,args.y2]

if not os.path.exists('False'): os.makedirs('False')
if not os.path.exists('True'): os.makedirs('True')

(startX, startY) = naip.deg2tile(topLeft[0],topLeft[1],zoomlevel)
(endX, endY) = naip.deg2tile(bottomRight[0],bottomRight[1],zoomlevel)
for x in range(startX, endX):
	yrange = range(startY, endY)
	urls = map(lambda y: naip.getUrl(x,y,zoomlevel), yrange)
	rs = (grequests.get(u) for u in urls)
	reses = grequests.map(rs, stream=True, size=25)
	for index, res in enumerate(reses):
		y = yrange[index]
		print (x, y)
		(left,top) = naip.tile2deg(x, y, zoomlevel)
		(right,bottom) = naip.tile2deg(x+1, y+1, zoomlevel)
		cur.execute("select * from buildings where x < (%s) and x > (%s) and y < (%s) and y > (%s);",(right, left, top, bottom))
		building = cur.fetchone() != None
		file = open("%s/%s_%s.jpg" % (building,x, y), 'w')
		shutil.copyfileobj(res.raw, file)     

