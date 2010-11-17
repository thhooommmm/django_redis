import redis

from django.conf import settings
from django.core.cache.backends.base import BaseCache

REDIS_PREFIX = getattr(settings, 'REDIS_CACHE_PREFIX', '')

class CacheClass(BaseCache):
    def __init__(self, server, params):
        BaseCache.__init__(self, params)
        self.server = redis.Redis(
            host=server.split(':')[0],
            port=server.split(':')[1],
            db=params.get('db',0)
        )


    def prefix(self, key):
        return '%s%s' % (
            REDIS_PREFIX,
            key
        )


    def add(self, key, value, timeout=None):
        if self.server.exists(key):
            return False
        else:
            self.set(key,value,timeout)
            return True


    def get(self, key, default=None):
        return self.server.get(key) or default


    def set(self, key, value, timeout=None):
        self.server.set(key, value)
        if timeout is not None:
            self.server.expire(key, timeout)


    def delete(self, key):
        self.server.delete(self.prefix(key))
