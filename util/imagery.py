# ----------------------------------------------
# Downloads imagery from tileserver
# ----------------------------------------------
import urllib2
import json
import sys
from cred import *
import math

# always fetch a fresh url template when module is loaded
req = urllib2.Request('https://api.trimblemaps.com/services.json?per_page=3&client_id=TEST')
req.add_header('X-API-TOKEN', CRED['naip_tiles_key'])
resp = urllib2.urlopen(req)
ata = json.loads(resp.read())
template = ata['items'][0]['tile_url_templates'][0] #naip

def fetchTile(x,y,zoom):
	try:
		url = template.replace("${x}", str(x)).replace("${y}", str(y)).replace("${z}", str(zoom))
		resp = urllib2.urlopen(url)
		return resp.read()
	except urllib2.HTTPError, err:
		return None
	except urllib2.URLError, err:
		return None