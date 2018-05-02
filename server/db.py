# ----------------------------------------------
# Db Helper for flask server, starts connections
# ----------------------------------------------
import psycopg2
from cred import *

# connect to the training data and predictions database
conn = psycopg2.connect(
	database=CRED['db']['db'],
	user = CRED['db']['user'],
	password = CRED['db']['pass'],
	host = CRED['db']['host']
)
cur = conn.cursor()

# connect to OSM mirror database (only when running in AWS)
if CRED['dev'] != "true":
	osmconn = psycopg2.connect(
		database="osm",
		user = CRED['osm']['user'],
		password = CRED['osm']['pass'],
		host = CRED['osm']['host']
	)
	osmcur = osmconn.cursor()