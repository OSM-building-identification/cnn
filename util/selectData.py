import os
import argparse
from random import *
import shutil

parser = argparse.ArgumentParser(description='Input sourcedir')
parser.add_argument("dir", help = "path to fir", type = str)
args = parser.parse_args()
outdir = './data'

cats = ['True', 'False']
segments = {
	'train' : 0.8,
	'test' : 0.4
}

odirs = []
for segment in segments:
	for cat in cats:
		odirs.append(os.path.join(segment, cat))

categories = os.listdir(args.dir)
if all(cat in categories for cat in cats):
	for dirp in odirs:
		path = os.path.join(outdir, dirp)
		if not os.path.exists(path): os.makedirs(path)

	for cat in cats:
		inpath = os.path.join(args.dir, cat)
		imgs = os.listdir(inpath)
		for img in imgs:
			segment = False
			while segment == False:
				for seg in segments:
					if random() < segments[seg]:
						segment = seg
			path = os.path.join(outdir, segment, cat)
			if not os.path.isfile(path):
				shutil.copy(os.path.join(inpath, img), path)
else:
	print "Missing Dir for a category..."
