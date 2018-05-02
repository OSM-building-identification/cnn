# ----------------------------------------------
# Routes for proxying OSM db requests
# ----------------------------------------------
import json
import psycopg2

from db import *

def init(app, auth):
	# -------------------
	# OSM Query Proxy
	# -------------------
	@app.route("/osm",  methods = ['POST'])
	@auth.login_required
	def osm():
		try:
			osmcur.execute( request.form["query"])
			res = osmcur.fetchmany(50);
			return json.dumps(res)
		except psycopg2.Error as e:
			osmconn.rollback()
			return str(e), 500
