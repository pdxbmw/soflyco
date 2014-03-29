from flask import Flask
from flask.ext.mongoengine import MongoEngine

from sofly.apps.common.session import MongoSessionInterface
from sofly.utils.security import SecurityUtils


db = MongoEngine()
log = app.logger
security = SecurityUtils()
mail = MailUtils()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    app.session_interface = MongoSessionInterface()

    db.init_app(app)

    from sofly.apps.results.views import module as results_module
    app.register_blueprint(results_module)

    from sofly.apps.search.views import module as search_module
    app.register_blueprint(search_module)
    
    from sofly.apps.users.views import module as users_module
    app.register_blueprint(users_module)    

    #import sofly.apps.common.filters
    #import sofly.apps.common.session
    #import sofly.views    

    return app

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