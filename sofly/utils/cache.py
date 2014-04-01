from werkzeug.contrib.cache import MemcachedCache

import hashlib

class CacheUtils(object):
    
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.cache = MemcachedCache(servers=app.config.get('MEMCACHE_SERVERS'))
    
    def delete(self, key):
        cache_key = hashlib.sha1(key).hexdigest()
        return self.cache.delete(cache_key)

    def get(self, key):
        cache_key = hashlib.sha1(key).hexdigest()
        return self.cache.get(cache_key)

    def set(self, key, value, **kwargs):
        cache_key = hashlib.sha1(key).hexdigest()
        self.cache.set(cache_key, value, timeout=kwargs.get('timeout',3600))