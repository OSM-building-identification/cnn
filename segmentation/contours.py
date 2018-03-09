import cv2
from PIL import Image
from PIL import ImageDraw

img = cv2.imread('mask.png',0)
rst,thresh = cv2.threshold(img,150,255,0)#cv2.adaptiveThreshold(img, 255, adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C, thresholdType=cv2.THRESH_BINARY, blockSize=7, C=0)
(img, contours, hier) = cv2.findContours(thresh, 1, cv2.CHAIN_APPROX_SIMPLE)
print cv2.CHAIN_APPROX_SIMPLE

i = Image.fromarray(img).convert('RGB')
drw = ImageDraw.Draw(i, "RGBA")

for contour in contours:
	rect = cv2.minAreaRect(contour)
	box = cv2.boxPoints(rect)
	boxpts = [(p[0], p[1]) for p in box]
	epsilon = 0.02*cv2.arcLength(contour,True)
	approx = cv2.approxPolyDP(contour,epsilon,True)
	approxpnts = [(p[0][0], p[0][1]) for p in contour]
	print approxpnts
	try:
		drw.polygon(boxpts, fill=(255,0,0,128))
	except TypeError:
		print "draw err"


i.show()
