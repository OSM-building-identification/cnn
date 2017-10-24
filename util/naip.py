import urllib2
import json
import sys
from cred import *
import math

# always fetch a fresh url template
req = urllib2.Request('https://api.trimblemaps.com/services.json?per_page=3&client_id=TEST')
req.add_header('X-API-TOKEN', CRED['naip_tiles_key'])
resp = urllib2.urlopen(req)
ata = json.loads(resp.read())
template = ata['items'][0]['tile_url_templates'][0]

def fetchTile(x,y,zoom):
	url = template.replace("${x}", str(x)).replace("${y}", str(y)).replace("${z}", str(zoom))
	resp = urllib2.urlopen(url)
	return resp.read()

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

def isInTile(lon, lat, xtile, ytile, zoom):
	(left,top) = tile2deg(xtile, ytile, zoom)
	(right,bottom) = tile2deg(xtile+1, ytile+1, zoom)
	return left <= lon and right >= lon and top >= lat and bottom <= lat

def featureInTile(feature, xtile, ytile, zoom):
	coord = feature['geometry']['coordinates'][0][0]
	return isInTile(coord[0], coord[1], xtile, ytile, zoom)