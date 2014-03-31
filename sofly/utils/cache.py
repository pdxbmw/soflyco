from flask import current_app

from Crypto.Cipher import AES
from werkzeug.contrib.cache import MemcachedCache
import bmemcached
import hashlib
import os

class CacheUtils(object):
    USERNAME = 'memcached-flights-pdxbmw'
    PASSWORD = 'Ct3NYpnCDHqohseV'
    URL      = 'pub-memcache-17464.us-east-1-4.1.ec2.garantiadata.com:17464'

    def __init__(self):
        self.cache = MemcachedCache(current_app.MEMCACHE_SERVERS)

        '''
        self.IS_DEV = app.config.get('IS_DEV')
        if self.IS_DEV:
            self.cache = MemcachedCache(['127.0.0.1:11211'])
        else:
            self.cache = bmemcached.Client(
                    os.environ.get('MEMCACHEDCLOUD_SERVERS')  or self.URL, 
                    os.environ.get('MEMCACHEDCLOUD_USERNAME') or self.USERNAME, 
                    os.environ.get('MEMCACHEDCLOUD_PASSWORD') or self.PASSWORD    
            )
        '''
    
    def delete(self, key):
        cache_key = hashlib.sha1(key).hexdigest()
        return self.cache.delete(cache_key)

    def get(self, key):
        cache_key = hashlib.sha1(key).hexdigest()
        return self.cache.get(cache_key)

    def set(self, key, value, **kwargs):
        cache_key = hashlib.sha1(key).hexdigest()
        if self.IS_DEV:
            self.cache.set(cache_key, value, timeout=kwargs.get('timeout',3600))
        else:
            self.cache.set(cache_key, value, time=kwargs.get('timeout',3600))