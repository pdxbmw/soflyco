"""

    Helpers module

"""

import json
import os
import pkgutil
import importlib

from flask import Blueprint, Config, Flask as BaseFlask, request, url_for

def register_blueprints(app, package_name, package_path):
    """
    Register all Blueprint instances on the specified Flask application found
    in all modules for the specified package.

    :param app: the Flask application
    :param package_name: the package name
    :param package_path: the package path
    """ 
    rv = []
    for _, name, _ in pkgutil.iter_modules(package_path):
        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
            rv.append(item)
    return rv

def _get_link(route, payload):
    ctx = app.test_request_context()
    ctx.push()
    url = url_for(route, payload=payload, _external=True)            
    ctx.pop()
    return url   

def get_activation_link(_id):
    from sofly import security
    s = security.get_serializer()
    payload = s.dumps(str(_id))
    return _get_link(route='users.activate_user', payload=payload)

def get_claim_link(identifier, email, price):    
    from sofly import security
    s = security.get_serializer()
    payload = s.dumps((identifier, email, price))
    return _get_link(route='results.claim', payload=payload)

def load_json_file(filename):
    basedir = os.path.abspath(os.path.dirname(__file__))
    f = open(os.path.join(basedir, 'static/json/%s.json' % filename))
    content = json.loads(f.read())
    f.close() 
    return content

def is_ajax(request):
    return 'XMLHttpRequest' in request.headers.get('X-Requested-With','')

def redirect_url(default='index'):
    print 'redirecting'
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)
           

class Flask(BaseFlask):
    """
    Extended version of `Flask` that implements custom config class
    and adds `register_middleware` method
    """

    def make_config(self, instance_relative=False):
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        return Config(root_path, self.default_config)

    def register_middleware(self, middleware_class):
        """
        Register a WSGI middleware on the application
        :param middleware_class: A WSGI middleware implementation
        """
        self.wsgi_app = middleware_class(self.wsgi_app)           

class FlashMessage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, category='info', payload=None):
        Exception.__init__(self)
        self.category = category
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv    