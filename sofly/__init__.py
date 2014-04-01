from flask.ext.mongoengine import MongoEngine
from werkzeug.contrib.fixers import ProxyFix

from sofly.helpers import Flask
from sofly.middleware import MethodRewriteMiddleware
from sofly.session import MongoSessionInterface
from sofly.utils.cache import CacheUtils
from sofly.utils.mail import MailUtils
from sofly.utils.security import SecurityUtils

from logging.handlers import SysLogHandler
from config import config

import logging
import os
import sys

cache = CacheUtils()
db = MongoEngine()
mail = MailUtils()
security = SecurityUtils()

os.environ['BASE_DIR'] = os.path.abspath(os.path.dirname(__file__))

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    #app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)
    app.wsgi_app = ProxyFix(app.wsgi_app)    

    syslog_handler = SysLogHandler()
    syslog_handler.setLevel(logging.DEBUG)
    #logging.basicConfig(stream=sys.stderr)
    app.logger.addHandler(syslog_handler)

    # production
    #sys.path.insert(0,"/var/www/sofly/")
    
    app.session_interface = MongoSessionInterface(app)
    
    cache.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    security.init_app(app)

    register_blueprints(app)

    @app.before_request
    def before_request():
        """
        Pull user's profile from the database before every request are treated
        """
        from flask import g, session
        from bson import ObjectId
        from sofly.modules.users.models import User
        g.user = None
        if 'user_id' in session:
            g.user = User.objects.get(id=ObjectId(session['user_id']))    

    return app

def register_blueprints(app):
    from sofly.modules.views import module as base_module
    from sofly.modules.errors import module as errors_module
    from sofly.modules.filters import module as filters_module
    from sofly.modules.results.views import module as results_module
    from sofly.modules.search.views import module as search_module
    from sofly.modules.users.views import module as users_module

    app.register_blueprint(base_module)
    app.register_blueprint(errors_module)
    app.register_blueprint(filters_module)
    app.register_blueprint(results_module)
    app.register_blueprint(search_module)
    app.register_blueprint(users_module)    
    

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