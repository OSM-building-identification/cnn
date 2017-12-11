import json
import os

# load credentials from ../cred.json
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
f = open(os.path.join(__location__, '..', 'cred.json'), 'r')
CRED = json.loads(f.read());
