import psycopg2
import requests
import json
from cred import *

# OSM db connection 
if CRED['dev'] != 'true':
	osm = psycopg2.connect(
		database="osm",
		user = CRED['osm']['user'],
		password = CRED['osm']['pass'],
		host = CRED['osm']['host']
	)
	osmcur = osm.cursor()

# app db connection
conn = psycopg2.connect(
	database=CRED['db']['db'],
	user = CRED['db']['user'],
	password = CRED['db']['pass'],
	host = CRED['db']['host']
)
cur = conn.cursor()

# isomorphic function for querying the osm database both on aws and locally
def queryosm(query):
	if CRED['dev'] == 'true':
		r = requests.post(
			CRED['http']['remote-host']+'osm',
			data = {'query':query},
			auth=('a', CRED['http']['pass'])
		)
		if(r.status_code == 200):
			return json.loads(r.text)
		else:
			raise Exception(r.text)
	else:
		osmcur.execute(query)
		res = osmcur.fetchmany(50);
		return json.loads(json.dumps(res))