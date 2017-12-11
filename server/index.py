from flask import Flask
from flask import jsonify
from flask import send_file
from flask_cors import CORS
from cred import *
import psycopg2

app = Flask(__name__)
CORS(app)


conn = psycopg2.connect(
	database="cucapstone",
	user = "cucapstone",
	password = CRED['db']['pass'],
	host = CRED['db']['host']
)
cur = conn.cursor()



@app.route("/")
def all():
	cur.execute('select x,y from training_tiles;')
	a=cur.fetchall()
	return jsonify(a)

@app.route("/t/<int:x>/<int:y>")
def tile(x, y):
	path = '../../tiles/%s_%s.jpg' % (x,y)
	return send_file(path, mimetype='image/jpg')

@app.route("/unverified")
def unver():
	cur.execute('select x,y from training_tiles where verified=false;')
	a=cur.fetchall()
	return jsonify(a)

@app.route("/verify/<int:x>/<int:y>/<string:building>")
def verify(x, y, building):
	is_building = building=='true'
	print (x,y,is_building)
	cur.execute('update training_tiles set verified=true, has_building=%s where x=%s and y=%s' % (is_building, x, y))
	conn.commit()
	return ""