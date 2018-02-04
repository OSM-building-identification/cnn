import sys
sys.path.append('util')

from PIL import Image
from PIL import ImageDraw

from db import *
import json
import naip

#queryosm("select exists(select 1 from building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326))" % (right, bottom, left, top))



def getMask(startX,startY, zoomlevel):
	endX = startX+1
	endY = startY+1

	(left,top) = naip.tile2deg(startX, startY, zoomlevel)
	(right,bottom) = naip.tile2deg(endX, endY, zoomlevel)
	buildings = queryosm("SELECT ST_AsGeoJSON(geometry) FROM building_polygon where geometry && ST_MakeEnvelope(%s, %s, %s, %s, 4326)" % (right, bottom, left, top))
	xLength = abs(left-right)
	yLength = abs(top-bottom)
	
	img = Image.new("RGB", (256,256), (0,0,0))
	drw = ImageDraw.Draw(img, "RGBA")
	
	for rawbuilding in buildings:
		building = json.loads(rawbuilding[0])
			 
		buildingCoord = [((buildingX-left)/xLength*255,(top-buildingY)/yLength*255) for (buildingX,buildingY) in building["coordinates"][0]]
		drw.polygon(buildingCoord, (255,255,255,255))
	img.show()           
	
(x,y) = naip.deg2tile(-105.283, 40.026, 17)
getMask(x,y,17)

