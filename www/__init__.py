from flask.ext.assets import Environment, Bundle
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
from werkzeug.contrib.fixers import ProxyFix

from www import assets
from www.helpers import Flask
from www.middleware import MethodRewriteMiddleware
from www.session import MongoSessionInterface
from www.utils.cache import CacheUtils
from www.utils.mail import MailUtils
from www.utils.security import SecurityUtils

from logging.handlers import SysLogHandler
from config import config

import logging
import os
import sys

# debug toolbar
from flask_debugtoolbar import DebugToolbarExtension

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
    #app.url_map.default_subdomain = 'www'  

    syslog_handler = SysLogHandler()
    syslog_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(syslog_handler)
    
    #app.session_interface = MongoSessionInterface(app)
    
    assets.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    security.init_app(app)

    app.session_interface = MongoEngineSessionInterface(db)

    register_blueprints(app)

    # debug toolbar
    """
    app.config['DEBUG_TB_PROFILER_ENABLED'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
    app.config['DEBUG_TB_PANELS'] = (
                'flask_debugtoolbar.panels.versions.VersionDebugPanel',
                'flask_debugtoolbar.panels.timer.TimerDebugPanel',
                'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
                'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
                'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
                'flask_debugtoolbar.panels.template.TemplateDebugPanel',
                #'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
                'flask_debugtoolbar.panels.logger.LoggingPanel',
                'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
                'flask.ext.mongoengine.panels.MongoDebugPanel'
            )
    toolbar = DebugToolbarExtension(app)    
    """

    @app.before_request
    def before_request():    
        """
        Pull user's profile from the database before every request are treated
        """
        from flask import g, session
        from bson import ObjectId
        from www.modules.users.models import User
        g.user = None
        if 'user_id' in session:
            g.user = User.objects.get(id=ObjectId(session['user_id']))    

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')       

    return app

def register_blueprints(app):
    from www.modules.views import module as base_module
    from www.modules.errors import module as errors_module
    from www.modules.filters import module as filters_module
    from www.modules.results.views import module as results_module
    from www.modules.search.views import module as search_module
    from www.modules.users.views import module as users_module

    app.register_blueprint(base_module)
    app.register_blueprint(errors_module)
    app.register_blueprint(filters_module)
    app.register_blueprint(results_module)
    app.register_blueprint(search_module)
    app.register_blueprint(users_module)    
    

#import sofly.apps.common.filters
#import sofly.apps.common.session
#import sofly.views    

#from www import config
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