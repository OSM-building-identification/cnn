import numpy as np

def getPointAngle(point):
	return np.arctan2(point[1], point[0])

def getSegmentAngle(segment):
	i = segment[0]
	j = segment[1]
	jtranslate = (j[0]-i[0], j[1]-i[1])
	return getPointAngle(jtranslate)

def getSegFromContour(contour, indexes):
	return [contour[indexes[0]], contour[indexes[1]]]

def isConvexMax(theta, contour):
	start = contour[0]
	for point in contour[1:]:
		dtheta = (getSegmentAngle([start, point])-theta)%(np.pi*2)
		if dtheta >= np.pi:
			return False, point
	return True, None

def getProjMax(theta, contour):
	[x1, y1] = contour[0]
	[x2, y2] = [contour[0][0]+np.cos(theta), contour[0][1]+np.sin(theta)]
	maxnx = -1e100
	lastpoint = contour[2]
	lastproj = contour[2]
	for [x3,y3] in contour[2:]:
		dx = x2 - x1
		dy = y2 - y1
		d2 = dx*dx + dy*dy
		nx = ((x3-x1)*dx + (y3-y1)*dy) / d2
		projected = [int(dx*nx + x1), int(dy*nx + y1)]
		if maxnx <= nx and [x3,y3] != contour[-1]:
			maxnx = nx
			lastpoint = [x3,y3]
			lastproj = projected
		else:
			return lastpoint, lastproj

def sharpHull(theta, contour):
	hull = []
	while len(contour) > 2:
		hull.append(contour[0])
		m, mproj = getProjMax(theta, contour)
		uptomax = contour[:contour.index(m)-1]
		cmax, cmaxpnt = isConvexMax(theta, uptomax)
		if cmax:
			theta += np.pi/2
			contour = contour[contour.index(m):]
			hull.append(mproj)
		else:
			theta -= np.pi/2
			contour = contour[contour.index(cmaxpnt):]
			hull.append(cmaxpnt)
	hull.append(contour[-1])
	return hull
