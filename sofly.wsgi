#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/sofly/")

from sofly import create_app
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

application = app

if __name__ == '__main__':
    app.run()