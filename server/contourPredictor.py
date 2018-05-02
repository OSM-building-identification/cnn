# ----------------------------------------------
# Route for on demand contour prediction of tile
# ----------------------------------------------
import sys
sys.path.append('segmentation')

from flask import jsonify
from cStringIO import StringIO
from PIL import Image

import imagery
import tileMath
import predict

def init(app, auth):
	predict.load(False) #load the default weights
	# -------------------
	# On-Demand Contour prediction
	# -------------------
	@app.route("/contours/<int:x>/<int:y>")
	@auth.login_required
	def contours(x,y):
		z=17
		# get lat lng boundaries and size of tile
		(startX, startY) = tileMath.tile2deg(x,y,z)
		(endX, endY) = tileMath.tile2deg(x+1,y+1,z)
		dx = endX-startX
		dy = endY-startY

		# download tile
		img = imagery.fetchTile(x,y,z)
		file_jpgdata = StringIO(img)
		i = Image.open(file_jpgdata) 

		#get image mask and contours
		out = predict.predictMask(i)
		contours = predict.getContours(out)

		# transform contours from pixel space to lat lng space
		realContours = [ [[((float(x)/255)*dx)+startX, ((float(y)/255)*dy)+startY] for [x,y] in pointset] for pointset in contours]

		return jsonify(realContours)