import sys
sys.path.append('util')

import naip
from flask import Flask
from flask import jsonify
from flask import send_file
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from flask import request
from cred import *
import psycopg2
import json

app = Flask(__name__)
CORS(app)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_pw(username, password):
		if CRED['dev'] != "true":
			return str(CRED['http']['pass']) == password
		else:
			return True

conn = psycopg2.connect(
	database=CRED['db']['db'],
	user = CRED['db']['user'],
	password = CRED['db']['pass'],
	host = CRED['db']['host']
)
cur = conn.cursor()

if CRED['dev'] != "true":
	osmconn = psycopg2.connect(
		database="osm",
		user = CRED['osm']['user'],
		password = CRED['osm']['pass'],
		host = CRED['osm']['host']
	)
	osmcur = osmconn.cursor()

@app.route("/training_tiles")
@auth.login_required
def all():
	cur.execute('select x,y from training_tiles;')
	a=cur.fetchall()
	return jsonify(a)

@app.route("/t/<int:x>/<int:y>")
def tile(x, y):
	path = '../data/tiles/%s_%s.jpg' % (x,y)
	return send_file(path, mimetype='image/jpg')

@app.route("/unverified")
@auth.login_required
def unver():
	cur.execute('select x,y from training_tiles where verified=false;')
	a=cur.fetchall()
	return jsonify(a)

@app.route("/verify/<int:x>/<int:y>/<string:building>")
@auth.login_required
def verify(x, y, building):
	is_building = building=='true'
	print (x,y,is_building)
	cur.execute('update training_tiles set verified=true, has_building=%s where x=%s and y=%s' % (is_building, x, y))
	conn.commit()
	return ""

@app.route("/predictions")
@auth.login_required
def preds():
	cur.execute('select x,y from predictions')
	a=cur.fetchall()
	return jsonify(a)


@app.route("/pred_tiles",  methods = ['POST'])
@auth.login_required
def get_tiles():
	try:
		tiles = request.json
	except ValueError:
		return str(e), 500

	res = []
	for tile in tiles:
		data = tile.split(',')
		x = int(float(data[0]))
		y = int(float(data[1]))
		z = int(float(data[2]))
		(slng, slat) = naip.tile2deg(x,y,z)
		(elng, elat) = naip.tile2deg(x+1,y+1,z)
		(startX, startY) = naip.deg2tile(slng, slat, 17)
		(endX, endY) = naip.deg2tile(elng, elat, 17)

		cur.execute("select exists(select 1 from predictions where x>=%s and y>=%s and x<%s and y<%s and has_building=TRUE)",(startX, startY, endX, endY))
		(has_building, ) = cur.fetchone();

		res.append({
			'tile' : tile,
			'has_building' : has_building
		})

	return json.dumps(res)

def getTiles(slng, slat, elng, elat, z):
	(startX, startY) = naip.deg2tile(slng, slat, z)
	(endX, endY) = naip.deg2tile(elng, elat, z)
	res = []
	for x in range(startX, endX):
		for y in range(startY, endY):
			(tslng, tslat) = naip.tile2deg(x,y,z)
			(telng, telat) = naip.tile2deg(x+1,y+1,z)
			(tstartX, tstartY) = naip.deg2tile(tslng, tslat, 17)
			(tendX, tendY) = naip.deg2tile(telng, telat, 17)
			cur.execute("select exists(select 1 from predictions where x>=%s and y>=%s and x<%s and y<%s and has_building=TRUE)",(tstartX, tstartY, tendX, tendY))
			(has_building, ) = cur.fetchone();
			if has_building == True:
				res.append({
					'x' : x,
					'y' : y,
					'z' : z
				})
	return res

@app.route("/preds/<int:sx>/<int:sy>/<int:sz>")
@auth.login_required
def getPredTiles(sx,sy,sz):
	toGet = [(sx,sy,sz)]
	res = []
	while len(toGet) > 0 and len(res) < 1000:
		(x, y, z) = toGet.pop(0)
		ratio = 2**(17-z)
		startX = x*ratio
		startY = y*ratio
		size = ratio/2

		if z == 17:
			res.append((x,y,z))
		else:
			for xo in range(2):
				for yo in range(2):
					tstartX = startX+(size*xo)
					tstartY = startY+(size*yo)
					tendX = tstartX+size
					tendY = tstartY+size

					thisX = (x*2)+xo
					thisY = (y*2)+yo
					thisZ = z+1

					cur.execute("select count(*) from predictions where x>=%s and y>=%s and x<=%s and y<=%s and has_building=TRUE",(tstartX, tstartY, tendX, tendY))
					(count, ) = cur.fetchone();

					if count/float(size**2) < 0.5 and count/float(size**2) > 0:
						toGet.append((thisX, thisY, thisZ))
					elif count > 0:
						res.append((thisX, thisY, thisZ))

	return jsonify(res)

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

	