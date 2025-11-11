"""MongoDB cache backend. For usage details, see :ref:`Backends: MongoDB <mongodb>`.

.. automodsumm:: requests_cache.backends.mongodb
   :classes-only:
   :nosignatures:
"""

from datetime import timedelta
from logging import getLogger
from typing import Iterable, Mapping, Optional, Union

from pymongo import MongoClient
from pymongo.errors import OperationFailure

from .._utils import get_valid_kwargs
from ..policy.expiration import NEVER_EXPIRE, get_expiration_seconds
from ..serializers import SerializerType, bson_document_serializer
from . import BaseCache, BaseStorage

logger = getLogger(__name__)


class MongoCache(BaseCache):
    """MongoDB cache backend.
    By default, responses are partially serialized into a MongoDB-compatible document format.

    Args:
        db_name: Database name
        connection: :py:class:`~pymongo.mongo_client.MongoClient` object to reuse instead of creating a new one
        kwargs: Additional keyword arguments for :py:class:`~pymongo.mongo_client.MongoClient`
    """

    def __init__(
        self,
        db_name: str = 'http_cache',
        connection: MongoClient = None,
        decode_content: bool = True,
        serializer: Optional[SerializerType] = None,
        **kwargs,
    ):
        super().__init__(cache_name=db_name, **kwargs)
        skwargs = {'serializer': serializer, **kwargs} if serializer else kwargs
        self.responses: MongoDict = MongoDict(
            db_name,
            collection_name='responses',
            connection=connection,
            decode_content=decode_content,
            **skwargs,
        )
        self.redirects: MongoDict = MongoDict(
            db_name,
            collection_name='redirects',
            connection=self.responses.connection,
            serializer=None,
            **kwargs,
        )

    def get_ttl(self) -> Optional[int]:
        """Get the currently defined TTL value in seconds, if any"""
        return self.responses.get_ttl()

    def set_ttl(self, ttl: Union[int, timedelta], overwrite: bool = False):
        """Create or update a TTL index. Notes:

        * This will have no effect if TTL is already set
        * To overwrite an existing TTL index, use ``overwrite=True``
        * This may take some time to complete, depending on the size of your cache
        * Use ``ttl=None, overwrite=True`` to remove the TTL index
        """
        self.responses.set_ttl(ttl, overwrite=overwrite)


class MongoDict(BaseStorage):
    """A dictionary-like interface for a MongoDB collection

    Args:
        db_name: Database name
        collection_name: Collection name
        connection: :py:class:`~pymongo.mongo_client.MongoClient` object to reuse instead of creating a new one
        kwargs: Additional keyword arguments for :py:class:`~pymongo.mongo_client.MongoClient`
    """

    def __init__(
        self,
        db_name: str,
        collection_name: str = 'http_cache',
        connection: Optional[MongoClient] = None,
        serializer: Optional[SerializerType] = bson_document_serializer,
        **kwargs,
    ):
        super().__init__(serializer=serializer, **kwargs)
        connection_kwargs = get_valid_kwargs(MongoClient.__init__, kwargs)
        self.connection = connection or MongoClient(**connection_kwargs)
        self.collection = self.connection[db_name][collection_name]

    def get_ttl(self) -> Optional[int]:
        """Get the currently defined TTL value in seconds, if any"""
        idx_info = self.collection.index_information().get('ttl_idx', {})
        return idx_info.get('expireAfterSeconds')

    def set_ttl(self, ttl: Union[int, timedelta], overwrite: bool = False):
        """Create or update a TTL index, and ignore and log any errors due to dropping a nonexistent
        index or attempting to overwrite without ```overwrite=True``.
        """
        try:
            self._set_ttl(get_expiration_seconds(ttl), overwrite=overwrite)
        except OperationFailure:
            logger.warning('Failed to update TTL index', exc_info=True)

    def _set_ttl(self, ttl: int, overwrite: bool = False):
        if overwrite:
            self.collection.drop_index('ttl_idx')
            logger.info('Dropped TTL index')

        if ttl and ttl != NEVER_EXPIRE:
            logger.info(f'Creating TTL index for {ttl} seconds')
            self.collection.create_index('created_at', name='ttl_idx', expireAfterSeconds=ttl)

    def __getitem__(self, key):
        result = self.collection.find_one({'_id': key})
        if result is None:
            raise KeyError
        value = result['data'] if 'data' in result else result
        return self.deserialize(key, value)

    def __setitem__(self, key, value):
        """If ``value`` is already a dict, its values will be stored under top-level keys.
        Otherwise, it will be stored under a 'data' key.
        """
        value = self.serialize(value)
        if not isinstance(value, Mapping):
            value = {'data': value}
        self.collection.replace_one({'_id': key}, value, upsert=True)

    def __delitem__(self, key):
        result = self.collection.find_one_and_delete({'_id': key}, {'_id': True})
        if result is None:
            raise KeyError

    def __len__(self):
        return self.collection.estimated_document_count()

    def __iter__(self):
        for d in self.collection.find({}, {'_id': True}):
            yield d['_id']

    def bulk_delete(self, keys: Iterable[str]):
        """Delete multiple keys from the cache. Does not raise errors for missing keys."""
        self.collection.delete_many({'_id': {'$in': list(keys)}})

    def clear(self):
        self.collection.drop()

    def close(self):
        self.connection.close()
