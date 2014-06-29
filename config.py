from authomatic.providers import oauth2
import authomatic
import copy
import os


class Config:
    ADMINS = frozenset(['admin@sofly.co'])
    DEFAULTS = {}

    APP_SECRET = '6qa!&S2YG^@@H7VfVayg5Hp&ZHrS2UGxfkRSbJb*%Zy!nNKqrtyfFckM2CWJWnep'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fwks!!4JZ5h!sxw&rv@3QdprsVh$pV2uX#Rzwx&eBW&XU9xz@9!ANQ@4ZfSxR8'

    CACHE_USERNAME = 'memcached-flights-pdxbmw'
    CACHE_PASSWORD = 'Ct3NYpnCDHqohseV'
    CACHE_URL      = 'pub-memcache-17464.us-east-1-4.1.ec2.garantiadata.com:17464'

    CSRF_ENABLED = True
    CSRF_SESSION_KEY = 'q%DC3uGPn5RsYHekDVs2d9Yv^#q#5j$HwjXK6nc#2qErD5rft3ADcHCuv7T&J7WD'

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

    MAIL_USERNAME = os.environ.get('MAIL_SENDER') or 'admin@sofly.co'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'dGMPyJ2a7%HszA^ga6@D'
    MAIL_HOST = os.environ.get('MAIL_HOST') or 'smtp.zoho.com:465'

    MEMCACHE_SERVERS = os.environ.get('MEMCACHE_SERVERS', '127.0.0.1:11211')
    
    # FOR LATER 
    """
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_SENDER') or 'nobody@example.com'
    MAIL_FLUSH_INTERVAL = 3600 # one hour
    MAIL_ERROR_RECIPIENT = os.environ.get('MAIL_ERROR_RECIPIENT')    
    """
    
    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = '6LdvVvASAAAAAKdWAk9sKZBGIbLqLM1HpsTVGtfw'
    RECAPTCHA_PRIVATE_KEY = '6LdvVvASAAAAADuuvsxXEjTkaW3zYUmie9qoPHoF'
    RECAPTCHA_OPTIONS = {'theme': 'clean'}

    config = copy.deepcopy(OAUTH2)
    config['__defaults__'] = DEFAULTS    


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_DB = 'sofly'
    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    SERVER_NAME = 'local.sofly.co:5000'


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'secret'


class ProductionConfig(Config):
    MONGO_URL = os.environ.get('MONGO_URL')    
    MONGODB_DB = os.environ.get('MONGODB_DATABASE')
    MONGODB_HOST = os.environ.get('MONGODB_HOST')
    MONGODB_PORT = 27017 or int(os.environ.get('MONGODB_PORT', 27017))
    MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME', '')
    MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', '')
    RECAPTCHA_USE_SSL = True
    SERVER_NAME = 'sofly.co'    

config = {
    'development': DevelopmentConfig,
    'testing'    : TestingConfig,
    'production' : ProductionConfig,
    'default'    : DevelopmentConfig
}

'''
MONGO = {
    'username' : 'appfog',
    'password' : '1d155e97f4a71dbaecc75a79a95bd3cc',
    'hostname' : 'troup.mongohq.com',
    'port'     : 10077,
    'db'       : 'flights_pdxbmw'
}   
'''