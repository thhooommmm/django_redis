import redis

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_unicode
from django.contrib.sessions.backends.base import SessionBase, CreateError

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')
REDIS_PORT = getattr(settings, 'REDIS_PORT', 6379)
REDIS_DB = getattr(settings, 'REDIS_DB', 0)

def get_server():
    return redis.Redis(host=REDIS_HOST,port=REDIS_PORT,db=REDIS_DB)

class SessionStore(SessionBase):
    """
    Redis-backed Session Implementation.
    """

    def __init__(self, session_key):
        super(SessionStore,self).__init__(session_key)
        self.server = get_server()


    def load(self):
        self.decode(force_unicode(self.server.get(self.session_key)))
        self.create()
        return {}
            

    def create(self):
        while True:
            self.session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return


    def save(self, must_create=False):
        if must_create and self.exists(self.session_key):
            raise CreateError
        self.server.set(self.session_key, self.encode(self._get_session(no_load=must_create)))
        if self.get_expiry_age() is not None:
            self.expire(self.session_key, self.get_expiry_age())


    def exists(self, session_key):
        if self.server.exists(session_key):
            return True
        else:
            return False


    def delete(self, session_key=None):
        self.server.delete(session_key, self._session_key)
        
