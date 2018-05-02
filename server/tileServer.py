# ----------------------------------------------
# Simple Tile server, for use in manual-verifier
# ----------------------------------------------
from flask import send_file

def init(app, auth):
	@app.route("/t/<int:x>/<int:y>")
	def tile(x, y):
		path = '../data/tiles/%s_%s.jpg' % (x,y)
		return send_file(path, mimetype='image/jpg')

	@app.route("/mt/<int:x>/<int:y>")
	def mtile(x, y):
		path = '../data/masks/%s_%s.jpg' % (x,y)
		return send_file(path, mimetype='image/jpg')