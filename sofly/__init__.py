from flask import Flask
from flask.ext.mongoengine import MongoEngine

from sofly.apps.common.session import MongoSessionInterface
from sofly.utils.mail import MailUtils
from sofly.utils.security import SecurityUtils

from config import config

import logging
import sys

from logging.handlers import SysLogHandler

db = MongoEngine()
mail = MailUtils()
security = SecurityUtils()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    syslog_handler = SysLogHandler()
    syslog_handler.setLevel(logging.DEBUG)
    logging.basicConfig(stream=sys.stderr)
    app.logger.addHandler(syslog_handler)

    # production
    sys.path.insert(0,"/var/www/sofly/")
    
    app.session_interface = MongoSessionInterface(app.config['MONGODB_SETTINGS'])
    
    db.init_app(app)
    mail.init_app(app)
    security.init_app(app)

    return app

#import sofly.apps.common.filters
#import sofly.apps.common.session
#import sofly.views    

#from sofly import config
#from flask_debugtoolbar import DebugToolbarExtension
#from logging.handlers import RotatingFileHandler


#Funnel(app)

#app.config['DEBUG_TB_PROFILER_ENABLED'] = True
#app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
#app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
#toolbar = DebugToolbarExtension(app)

# debug logging
#file_handler = RotatingFileHandler('debug.log', maxBytes=10000, backupCount=1)
#file_handler.setLevel(logging.DEBUG)
#app.logger.addHandler(file_handler)