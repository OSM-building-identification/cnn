from flask import Flask
from flask import jsonify
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
