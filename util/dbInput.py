import json
import psycopg2

conn = psycopg2.connect("dbname=osm user=satchel")
cur = conn.cursor()

def add_building(osm_id, coordinate):
	cur.execute("insert into buildings (x, y, osm_id) values (%s, %s, %s);", (coordinate[0],coordinate[1],osm_id))

with open('building_polygon.json') as f:
		i=0
		for line in f:
				if line[0] == ',':
					line = line[1:]
				if line[0:3] == '{"t':
					feature = json.loads(line)
					type = feature['geometry']['type']
					osm_id = feature['properties']['osm_id']
					cur.execute("select * from buildings where osm_id = (%s);", (osm_id,))
					if cur.fetchone() == None:
						if type == 'Polygon':
							add_building(osm_id, feature['geometry']['coordinates'][0][0])
						elif type == 'MultiPolygon':
							for poly in feature['geometry']['coordinates']:
								add_building(osm_id, poly[0][0])
				i = i+1

conn.commit()
cur.close()
conn.close()