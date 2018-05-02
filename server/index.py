# --------------------------------------------------------
# Flask server for use by, osm proxy, iD and verifier apps
# --------------------------------------------------------
import sys
sys.path.append('util')

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS

from cred import *

# modules
import manualVerifier
import tileServer
import contourPredictor
import missingTiles
import dbProxy

app = Flask(__name__)
CORS(app)
auth = HTTPBasicAuth()

# basic auth when in production
@auth.verify_password
def verify_pw(username, password):
		if CRED['dev'] != "true":
			return str(CRED['http']['pass']) == password
		else:
			return True

# init all modules
manualVerifier.init(app, auth)
tileServer.init(app, auth)
contourPredictor.init(app, auth)
missingTiles.init(app, auth)
dbProxy.init(app, auth)
