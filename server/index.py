import sys
sys.path.append('util')

from flask import Flask
from flask import jsonify
from flask import send_file
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from db import *
import psycopg2

app = Flask(__name__)
CORS(app)
auth = HTTPBasicAuth()

@auth.get_password
def get_pw(username):
    return CRED['http']['pass']

@app.route("/training_tiles")
@auth.login_required
def all():
	cur.execute('select x,y from training_tiles;')
	a=cur.fetchall()
	return jsonify(a)

@app.route("/t/<int:x>/<int:y>")
@auth.login_required
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
	cur.execute('select x,y from predictions where has_building=true;')
	a=cur.fetchall()
	return jsonify(a)