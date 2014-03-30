#!/usr/bin/env python

from sofly import create_app

import os

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)