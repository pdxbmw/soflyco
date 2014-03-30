import os
import json

basedir = os.path.dirname(__file__)

f = open(os.path.join(basedir, 'data/airports.json'))
airports = json.loads(f.read())
f.close()