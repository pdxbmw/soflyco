#!/usr/bin/env python

from www import create_app

import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')  

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)