import os
import osm
import naip

import argparse

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

geojson = osm.fetchBuildings(topLeft, bottomRight)
buildings = geojson['features']
(startX, startY) = naip.deg2tile(topLeft[0],topLeft[1],zoomlevel)
(endX, endY) = naip.deg2tile(bottomRight[0],bottomRight[1],zoomlevel)
for x in range(startX, endX):
	for y in range(startY, endY):
		print (x,y)
		building = any(naip.featureInTile(building, x, y, zoomlevel) for building in buildings)
		img = naip.fetchTile(x,y,zoomlevel)
		file = open("%s/%s_%s.jpg" % (building,x, y), 'w')
		file.write(img)
			


