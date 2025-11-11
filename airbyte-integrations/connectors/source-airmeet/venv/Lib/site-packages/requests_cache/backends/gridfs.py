"""GridFS cache backend. For usage details, see :ref:`Backends: GridFS <gridfs>` and :ref:`Backends: MongoDB <mongodb>`.

.. automodsumm:: requests_cache.backends.gridfs
   :classes-only:
   :nosignatures:
"""

from logging import getLogger
from threading import RLock
from typing import Optional

from gridfs import GridFS
from gridfs.errors import CorruptGridFile, FileExists
from pymongo import MongoClient

from .._utils import get_valid_kwargs
from ..serializers import SerializerType, pickle_serializer
from .base import BaseCache, BaseStorage
from .mongodb import MongoDict

logger = getLogger(__name__)


class GridFSCache(BaseCache):
    """GridFS cache backend.

    Args:
        db_name: Database name
        connection: :py:class:`~pymongo.mongo_client.MongoClient` object to reuse instead of creating a new one
        kwargs: Additional keyword arguments for :py:class:`~pymongo.mongo_client.MongoClient`
    """

    def __init__(
        self,
        db_name: str,
        decode_content: bool = False,
        serializer: Optional[SerializerType] = None,
        **kwargs,
    ):
        super().__init__(cache_name=db_name, **kwargs)
        skwargs = {'serializer': serializer, **kwargs} if serializer else kwargs

        self.responses = GridFSDict(db_name, decode_content=decode_content, **skwargs)
        self.redirects = MongoDict(
            db_name,
            collection_name='redirects',
            connection=self.responses.connection,
            serializer=None,
            **kwargs,
        )

    def delete(self, *args, **kwargs):
        with self.responses._lock:
            return super().delete(*args, **kwargs)


class GridFSDict(BaseStorage):
    """A dictionary-like interface for a GridFS database

    Args:
        db_name: Database name
        collection_name: Ignored; GridFS internally uses collections 'fs.files' and 'fs.chunks'
        connection: :py:class:`~pymongo.mongo_client.MongoClient` object to reuse instead of creating a new one
        kwargs: Additional keyword arguments for :py:class:`~pymongo.mongo_client.MongoClient`
    """

    def __init__(
        self,
        db_name,
        collection_name=None,
        connection=None,
        serializer: Optional[SerializerType] = pickle_serializer,
        **kwargs,
    ):
        super().__init__(serializer=serializer, **kwargs)
        connection_kwargs = get_valid_kwargs(MongoClient.__init__, kwargs)
        self.connection = connection or MongoClient(**connection_kwargs)
        self.db = self.connection[db_name]
        self.fs = GridFS(self.db)
        self._lock = RLock()

    def __getitem__(self, key):
        try:
            with self._lock:
                result = self.fs.find_one({'_id': key})
                if result is None:
                    raise KeyError
                return self.deserialize(key, result.read())
        except CorruptGridFile as e:
            logger.warning(e, exc_info=True)
            raise KeyError from e

    def __setitem__(self, key, item):
        value = self.serialize(item)
        encoding = None if isinstance(value, bytes) else 'utf-8'

        with self._lock:
            try:
                self.fs.delete(key)
                self.fs.put(value, encoding=encoding, **{'_id': key})
            # This can happen because GridFS is not thread-safe for concurrent writes
            except FileExists as e:
                logger.warning(e, exc_info=True)

    def __delitem__(self, key):
        with self._lock:
            res = self.fs.find_one({'_id': key})
            if res is None:
                raise KeyError
            self.fs.delete(res._id)

    def __len__(self):
        return self.db['fs.files'].estimated_document_count()

    def __iter__(self):
        for d in self.fs.find():
            yield d._id

    def clear(self):
        self.db['fs.files'].drop()
        self.db['fs.chunks'].drop()
