import os
import osm
import naip

zoomlevel = 16
topLeft = [-105.333227, 40.031642]
bottomRight = [-105.284818, 39.992856]

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
		
