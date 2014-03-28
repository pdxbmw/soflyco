from sofly import app
import json
import os 

f = open(os.path.join(app.root_path, 'data/airports.json'))
airports = json.loads(f.read())
f.close()