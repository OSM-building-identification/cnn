# -----------------------------
# Routes for Missing Tiles (iD)
# -----------------------------
from flask import jsonify
from flask import request

from db import *

#simple cached tile fetch
cache = {}
def getTilesCached(bounds):
	if bounds in cache:
		return cache[bounds]
	else:
		(tstartX, tstartY, tendX, tendY) = bounds
		cur.execute("select x,y,model,completed,incorrect from predictions where x>=%s and y>=%s and x<%s and y<%s and has_building=TRUE",(tstartX, tstartY, tendX, tendY))
		resTiles = cur.fetchall();
		cache[bounds] = resTiles
		return resTiles;

def init(app, auth):
	# ---------------------------
	# Missing Tiles Cluser Server
	# ---------------------------
	@app.route("/pred_tiles",  methods = ['POST'])
	@auth.login_required
	def get_tiles():
		try:
			tiles = request.json
		except ValueError:
			return str(e), 500

		out = {}
		for tile in tiles:
			sx = tile[0]
			sy = tile[1]
			sz = tile[2]

			toGet = [(sx,sy,sz)] #stack of tiles which still need to be founf
			res = {}
			while len(toGet) > 0 and len(res) < 20:
				(x, y, z) = toGet.pop(0)
				ratio = 2**(17-z)
				startX = x*ratio
				startY = y*ratio
				size = ratio/2

				# for each quadrand of tile
				for xo in range(2):
					for yo in range(2):
						tstartX = startX+(size*xo)
						tstartY = startY+(size*yo)
						tendX = tstartX+size
						tendY = tstartY+size

						thisX = (x*2)+xo
						thisY = (y*2)+yo
						thisZ = z+1
						resTiles = getTilesCached((tstartX, tstartY, tendX, tendY))
						count = len(resTiles)

						# if 17 then return tile, otherwise subdivide if we haven't gone too far already
						if(thisZ == 17):
							for restile in resTiles:
								(x,y,model,completed,incorrect) = restile
								res[str(x)+','+str(y)+',17'] = {
									'id' : str(x)+','+str(y)+',17',
									'coords' : [x,y,17],
									'model' : model,
									'completed' : completed,
									'incorrect' : incorrect
								}
						elif (sz >= 15 and count > 0) or (count/float(size**2) < 0.5 and count/float(size**2) > 0):
								toGet.append((thisX, thisY, thisZ))
						elif count > 0:
							res[str(thisX)+','+str(thisY)+','+str(thisZ)] = {
								'id' : str(thisX)+','+str(thisY)+','+str(thisZ),
								'coords' : [thisX, thisY, thisZ]
							}
					
			out[','.join(map(lambda n: str(n), tile))] = res

		return jsonify(out)