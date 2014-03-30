#!/usr/bin/python
from sofly import create_app

import os

def register_blueprints(app):
    # Prevents circular imports
    from sofly.apps.results.views import module as results_module
    from sofly.apps.search.views import module as search_module
    from sofly.apps.users.views import module as users_module
    
    app.register_blueprint(results_module)
    app.register_blueprint(search_module)
    app.register_blueprint(users_module)    

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    register_blueprints(app)
    app.run()