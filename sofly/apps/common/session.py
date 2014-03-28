import config
from flask.sessions import SessionInterface, SessionMixin
from datetime import datetime, timedelta
from pymongo import MongoClient, Connection
from uuid import uuid4
from werkzeug.datastructures import CallbackDict
#import config 
import os 


"""

    
    Securely store session data in MongoDB


"""


class MongoSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None):
        CallbackDict.__init__(self, initial)
        self.sid = sid
        self.modified = False

class MongoSessionInterface(SessionInterface):

    def __init__(self, host='localhost', port=27017, db='sofly', collection='sessions'):    
        if config.IS_DEV:
            uri = "mongodb://%s:%d/%s" % (host, port, db)   
        else:
            MONGO = config.MONGO
            uri = os.environ.get('MONGOHQ_URL')
            if not uri:
                uri = "mongodb://%s:%s@%s:%d/%s" % (
                    config.MONGO['username'],
                    config.MONGO['password'],
                    config.MONGO['hostname'],
                    config.MONGO['port'],
                    config.MONGO['db']
                )                        
        client = MongoClient(uri)
        self.store = client[db][collection]

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            stored_session = self.store.find_one({'sid': sid})
            if stored_session:
                if stored_session.get('expiration') > datetime.utcnow():
                    return MongoSession(initial=stored_session['data'],
                                        sid=stored_session['sid'])
        sid = str(uuid4())
        return MongoSession(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        now = datetime.utcnow()
        if not session:
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        if self.get_expiration_time(app, session):
            expiration = self.get_expiration_time(app, session)
        else:
            expiration = now + timedelta(hours=1)
        #self.store.ensure_index('expiration', expireAfterSeconds=3600) ## TEMPORARY    
        self.store.update({'sid': session.sid},
                          {'sid': session.sid,
                           'data': session,
                           'created': now,
                           'expiration': expiration}, True)
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=self.get_expiration_time(app, session),
                            httponly=True, domain=domain)