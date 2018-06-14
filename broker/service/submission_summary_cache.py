from expiringdict import ExpiringDict
from .exception.cache_miss_exception import CacheMissException

FIVE_MINUTES = 60 * 5
MAX_CACHE_SIZE = 10000


class SubmissionSummaryCache:

    def __init__(self, cache_size=None, expiry=None):
        self.cache_size = MAX_CACHE_SIZE if not cache_size else cache_size
        self.expiry = FIVE_MINUTES if not expiry else expiry

        self._cache = ExpiringDict(self.cache_size, self.expiry)

    def get(self, uuid):
        try:
            return self._cache[uuid]
        except KeyError:
            raise CacheMissException(uuid)

    def insert(self, uuid, summary):
        self._cache[uuid] = summary
