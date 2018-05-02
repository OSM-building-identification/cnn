# ---------------------------
# Routes for Manual verifier
# ---------------------------
from db import *
from flask import jsonify

def init(app, auth):
	# -------------------
	# Classifier Manual Verification
	# -------------------
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

	# -------------------
	# Segmentation Manual Verification
	# -------------------
	@app.route("/segmentation/unverified")
	@auth.login_required
	def unver_seg():
		cur.execute('select x,y from segmentation_training_tiles where verified=false;')
		a=cur.fetchall()
		return jsonify(a)

	@app.route("/segmentation_verify/<int:x>/<int:y>/<string:ok>/<string:dx>/<string:dy>")
	@auth.login_required
	def verifyseg(x, y, ok, dx, dy):
		is_ok = ok=='true'
		print (x,y,is_ok)
		cur.execute('update segmentation_training_tiles set verified=true, useable=%s, dx=%d, dy=%d where x=%s and y=%s' % (is_ok, int(dx), int(dy), x, y))
		conn.commit()
		return ""