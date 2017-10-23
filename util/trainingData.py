import os
import osm
import naip

zoomlevel = 17
topLeft = [-105.1,40.1]
bottomRight = [-105,40]

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
			def saveImage(img):
				file = open("%s/%s_%s.jpg" % (building,x, y), 'w')
				file.write(img)
			naip.fetchTile(x,y,saveImage)

osm.fetchBuildings(topLeft, bottomRight, handleFetch)
		
