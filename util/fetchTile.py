import urllib2
import json
import sys

# always fetch a fresh url template
req = urllib2.Request('https://api.trimblemaps.com/services.json?per_page=3&client_id=TEST')
req.add_header('X-API-TOKEN', sys.argv[1])
resp = urllib2.urlopen(req)
ata = json.loads(resp.read())
template = ata['items'][0]['tile_url_templates'][0].replace("${z}", '17')

def fetchTile(x,y):
	url = template.replace("${x}", str(x)).replace("${y}", str(y))
	resp = urllib2.urlopen(url)
	file = open("%s_%s.jpg" % (x, y), 'w')
	file.write(resp.read())

for x in range(2):
	for y in range(2):
		fetchTile(27500+x, 50001+y)