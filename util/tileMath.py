# ----------------------------------------------
# Helper functions for geo math with tiles
# ----------------------------------------------
import urllib2
import json
import math

# finds tile containing lat lng point at zoom level
def deg2tile(lon, lat, zoom):
	lat_rad = math.radians(lat)
	n = 2.0 ** zoom
	xtile = int((lon + 180.0) / 360.0 * n)
	ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
	return (xtile, ytile)

# tile's NW corner
def tile2deg(xtile, ytile, zoom):
	n = 2.0 ** zoom
	lon = xtile / n * 360.0 - 180.0
	lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
	lat = math.degrees(lat_rad)
	return (lon, lat)

# checks if point is in tile
def isInTile(lon, lat, xtile, ytile, zoom):
	(left,top) = tile2deg(xtile, ytile, zoom)
	(right,bottom) = tile2deg(xtile+1, ytile+1, zoom)
	return left <= lon and right >= lon and top >= lat and bottom <= lat

# checks if a feature intersects a tile
def featureInTile(feature, xtile, ytile, zoom):
	coord = feature['geometry']['coordinates'][0][0]
	return isInTile(coord[0], coord[1], xtile, ytile, zoom)
