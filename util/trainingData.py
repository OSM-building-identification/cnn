import os
import osm
import naip

import argparse

parser = argparse.ArgumentParser(description='Input longitude and lattitude')
parser.add_argument("x", help = "Enter the top most tile x value", type = float)
parser.add_argument("y", help = "Enter the top most tile y value", type = float)
parser.add_argument("x2", help = "Enter the bottom most tile x value", type = float)
parser.add_argument("y2", help = "Enter the bottom most tile y value", type = float)
parser.add_argument("zoom", help = "Enter the zoom value (usually 17)", type = int)
args = parser.parse_args()

zoomlevel = args.zoom
#topLeft = [-105.333227, 40.031642]
#bottomRight = [-105.284818, 39.992856]

topLeft = [args.x, args.y]
bottomRight = [args.x2,args.y2]

if not os.path.exists('False'): os.makedirs('False')
if not os.path.exists('True'): os.makedirs('True')

def handleFetch(geojson):
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



osm.fetchBuildings(topLeft, bottomRight, handleFetch)
