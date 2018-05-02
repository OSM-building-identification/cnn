# ----------------------------------------------
# load and parse credentials from cred.json
# ----------------------------------------------
import json
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
f = open(os.path.join(__location__, '..', 'cred.json'), 'r')
CRED = json.loads(f.read());
