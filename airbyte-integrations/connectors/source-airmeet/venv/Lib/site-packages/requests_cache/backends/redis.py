"""Redis cache backend. For usage details, see :ref:`Backends: Redis <redis>`.

.. automodsumm:: requests_cache.backends.redis
   :classes-only:
   :nosignatures:
"""

from logging import getLogger
from typing import Iterable, Optional

from redis import Redis, StrictRedis

from .._utils import get_valid_kwargs
from ..cache_keys import decode, encode
from ..serializers import SerializerType, pickle_serializer, utf8_encoder
from . import BaseCache, BaseStorage

DEFAULT_TTL_OFFSET = 3600
logger = getLogger(__name__)


class RedisCache(BaseCache):
    """Redis cache backend.

    Args:
        namespace: Redis namespace
        connection: Redis connection instance to use instead of creating a new one
        ttl: Use Redis TTL to automatically delete expired items
        ttl_offset: Additional time to wait before deleting expired items, in seconds
        kwargs: Additional keyword arguments for :py:class:`redis.client.Redis`
    """

    def __init__(
        self,
        namespace='http_cache',
        connection: Optional[Redis] = None,
        serializer: Optional[SerializerType] = None,
        ttl: bool = True,
        ttl_offset: int = DEFAULT_TTL_OFFSET,
        **kwargs,
    ):
        super().__init__(cache_name=namespace, **kwargs)
        skwargs = {'serializer': serializer, **kwargs} if serializer else kwargs
        self.responses = RedisDict(
            namespace, connection=connection, ttl=ttl, ttl_offset=ttl_offset, **skwargs
        )
        self.redirects = RedisHashDict(
            namespace, collection_name='redirects', connection=self.responses.connection, **kwargs
        )


class RedisDict(BaseStorage):
    """A dictionary-like interface for Redis operations.

    **Notes:**
        * All keys will be encoded as bytes, and all values will be serialized
        * Supports TTL
    """

    def __init__(
        self,
        namespace: str,
        collection_name: Optional[str] = None,
        connection=None,
        serializer: Optional[SerializerType] = pickle_serializer,
        ttl: bool = True,
        ttl_offset: int = DEFAULT_TTL_OFFSET,
        **kwargs,
    ):
        super().__init__(serializer=serializer, **kwargs)
        connection_kwargs = get_valid_kwargs(Redis.__init__, kwargs)
        self.connection = connection or StrictRedis(**connection_kwargs)
        self.namespace = namespace
        self.ttl = ttl
        self.ttl_offset = ttl_offset

    def _bkey(self, key: str) -> bytes:
        """Get a full hash key as bytes"""
        return encode(f'{self.namespace}:{key}')

    def _bkeys(self, keys: Iterable[str]):
        return [self._bkey(key) for key in keys]

    def __contains__(self, key) -> bool:
        return bool(self.connection.exists(self._bkey(key)))

    def __getitem__(self, key):
        result = self.connection.get(self._bkey(key))
        if result is None:
            raise KeyError
        return self.deserialize(key, result)

    def __setitem__(self, key, item):
        """Save an item to the cache, optionally with TTL"""
        expires_delta = getattr(item, 'expires_delta', None)
        ttl_seconds = (expires_delta or 0) + self.ttl_offset
        if self.ttl and ttl_seconds > 0:
            self.connection.setex(self._bkey(key), ttl_seconds, self.serialize(item))
        else:
            self.connection.set(self._bkey(key), self.serialize(item))

    def __delitem__(self, key):
        if not self.connection.delete(self._bkey(key)):
            raise KeyError

    def __iter__(self):
        yield from self.keys()

    def __len__(self):
        return len(list(self.keys()))

    def bulk_delete(self, keys: Iterable[str]):
        """Delete multiple keys from the cache, without raising errors for missing keys"""
        if keys:
            self.connection.delete(*self._bkeys(keys))

    def clear(self):
        self.bulk_delete(self.keys())

    def close(self):
        self.connection.close()

    def keys(self):
        return [
            decode(key).replace(f'{self.namespace}:', '')
            for key in self.connection.keys(f'{self.namespace}:*')
        ]

    def items(self):
        return [(k, self[k]) for k in self.keys()]

    def values(self):
        for _, v in self.items():
            yield v


class RedisHashDict(BaseStorage):
    """A dictionary-like interface for operations on a single Redis hash

    **Notes:**
        * All keys will be encoded as bytes
        * Items will be stored in a hash named ``namespace:collection_name``
    """

    def __init__(
        self,
        namespace: str = 'http_cache',
        collection_name: Optional[str] = None,
        connection=None,
        serializer: Optional[SerializerType] = utf8_encoder,
        **kwargs,
    ):
        super().__init__(serializer=serializer, **kwargs)
        connection_kwargs = get_valid_kwargs(Redis, kwargs)
        self.connection = connection or StrictRedis(**connection_kwargs)
        self._hash_key = f'{namespace}-{collection_name}'

    def __contains__(self, key):
        return self.connection.hexists(self._hash_key, encode(key))

    def __getitem__(self, key):
        result = self.connection.hget(self._hash_key, encode(key))
        if result is None:
            raise KeyError
        return self.deserialize(key, result)

    def __setitem__(self, key, item):
        self.connection.hset(self._hash_key, encode(key), self.serialize(item))

    def __delitem__(self, key):
        if not self.connection.hdel(self._hash_key, encode(key)):
            raise KeyError

    def __iter__(self):
        yield from self.keys()

    def __len__(self):
        return self.connection.hlen(self._hash_key)

    def bulk_delete(self, keys: Iterable[str]):
        """Delete multiple keys from the cache, without raising errors for missing keys"""
        if keys:
            self.connection.hdel(self._hash_key, *[encode(key) for key in keys])

    def clear(self):
        self.connection.delete(self._hash_key)

    def keys(self):
        return [decode(key) for key in self.connection.hkeys(self._hash_key)]

    def items(self):
        """Get all ``(key, value)`` pairs in the hash"""
        return [
            (decode(k), self.deserialize(decode(k), v))
            for k, v in self.connection.hgetall(self._hash_key).items()
        ]

    def values(self):
        """Get all values in the hash"""
        for _, v in self.items():
            yield v
