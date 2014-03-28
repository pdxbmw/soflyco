from authomatic.providers import oauth2
import authomatic
import copy
import os
    
_basedir = os.path.abspath(os.path.dirname(__file__))

DEFAULTS = { 'popup': True }
IS_DEV = 'agreisel' in _basedir

DEBUG = True

ADMINS = frozenset(['admin@sofly.co'])

APP_SECRET = '6qa!&S2YG^@@H7VfVayg5Hp&ZHrS2UGxfkRSbJb*%Zy!nNKqrtyfFckM2CWJWnep'
SECRET_KEY = 'fwks!!4JZ5h!sxw&rv@3QdprsVh$pV2uX#Rzwx&eBW&XU9xz@9!ANQ@4ZfSxR8'

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'q%DC3uGPn5RsYHekDVs2d9Yv^#q#5j$HwjXK6nc#2qErD5rft3ADcHCuv7T&J7WD'

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = '6LdvVvASAAAAAKdWAk9sKZBGIbLqLM1HpsTVGtfw'
RECAPTCHA_PRIVATE_KEY = '6LdvVvASAAAAADuuvsxXEjTkaW3zYUmie9qoPHoF'
RECAPTCHA_OPTIONS = {'theme': 'clean'}

OAUTH2 = {
    'facebook': {     
        'class_': oauth2.Facebook,
        'consumer_key': '427793563990619',
        'consumer_secret': '1925996e1d751d544d022b391102c337',
        'id': authomatic.provider_id(),
        'scope': oauth2.Facebook.user_info_scope + ['user_about_me', 'email']
    },
    'google': {
        'class_': oauth2.Google,
        'consumer_key': '348491297703-g4dk3hkankmvrnj17n57d66a5em6o82p.apps.googleusercontent.com',
        'consumer_secret': '9NQlgoRdMCMjWQPWCQoobr4J',
        'id': authomatic.provider_id(),
        'scope': oauth2.Google.user_info_scope + ['https://www.googleapis.com/auth/userinfo.email']
    }
}

MONGO = {
    'username' : 'appfog',
    'password' : '1d155e97f4a71dbaecc75a79a95bd3cc',
    'hostname' : 'troup.mongohq.com',
    'port'     : 10077,
    'db'       : 'flights_pdxbmw'
}

MONGODB_SETTINGS = {
    'USERNAME' : os.environ.get('MONGODB_USERNAME', ''),
    'PASSWORD' : os.environ.get('MONGODB_PASSWORD', ''),
    'HOST'     : os.environ.get('MONGODB_HOST', 'localhost'),
    'PORT'     : int(os.environ.get('MONGODB_PORT', 27017)),
    'NAME'       : os.environ.get('MONGODB_DATABASE', 'sofly')
}

config = copy.deepcopy(OAUTH2)
config['__defaults__'] = DEFAULTS