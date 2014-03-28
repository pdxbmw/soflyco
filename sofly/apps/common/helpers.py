from flask import request, url_for

from sofly import app, log, security

def _get_link(route, payload):
    ctx = app.test_request_context()
    ctx.push()
    url = url_for(route, payload=payload, _external=True)            
    ctx.pop()
    return url

def get_activation_link(_id):
    s = security.get_serializer()
    payload = s.dumps(str(_id))
    return _get_link(route='users.activate_user', payload=payload)

def get_claim_link(identifier, email, price):    
    s = security.get_serializer()
    payload = s.dumps((identifier, email, price))
    return _get_link(route='results.claim', payload=payload)

def redirect_url(default='index'):
    print 'redirecting'
    log.debug((request.args.get('next'), request.referrer, url_for(default)))
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

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