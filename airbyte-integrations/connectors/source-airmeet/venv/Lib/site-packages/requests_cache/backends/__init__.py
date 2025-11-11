"""Classes and functions for cache persistence. See :ref:`backends` for general usage info."""

# ruff: noqa: F401
from logging import getLogger
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional, Type, Union

from .._utils import get_placeholder_class, get_valid_kwargs
from .base import BaseCache, BaseStorage, DictStorage

# Backend-specific keyword arguments equivalent to 'cache_name'
CACHE_NAME_KWARGS = ['db_path', 'db_name', 'namespace', 'table_name']

BackendSpecifier = Union[str, BaseCache]
StrOrPath = Union[Path, str]
logger = getLogger(__name__)


# Import all backend classes for which dependencies are installed
try:
    from .dynamodb import DynamoDbCache, DynamoDbDict
except ImportError as e:
    DynamoDbCache = DynamoDbDict = get_placeholder_class(e)  # type: ignore

try:
    from .gridfs import GridFSCache, GridFSDict
except ImportError as e:
    GridFSCache = GridFSDict = get_placeholder_class(e)  # type: ignore

try:
    from .mongodb import MongoCache, MongoDict
except ImportError as e:
    MongoCache = MongoDict = get_placeholder_class(e)  # type: ignore

try:
    from .redis import RedisCache, RedisDict, RedisHashDict
except ImportError as e:
    RedisCache = RedisDict = RedisHashDict = get_placeholder_class(e)  # type: ignore

try:
    from .sqlite import SQLiteCache, SQLiteDict
except ImportError as e:
    SQLiteCache = SQLiteDict = get_placeholder_class(e)  # type: ignore

try:
    from .filesystem import FileCache, FileDict
except ImportError as e:
    FileCache = FileDict = get_placeholder_class(e)  # type: ignore


BACKEND_CLASSES = {
    'dynamodb': DynamoDbCache,
    'filesystem': FileCache,
    'gridfs': GridFSCache,
    'memory': BaseCache,
    'mongodb': MongoCache,
    'redis': RedisCache,
    'sqlite': SQLiteCache,
}


def init_backend(
    cache_name: StrOrPath, backend: Optional[BackendSpecifier] = None, **kwargs
) -> BaseCache:
    """Initialize a backend from a name, class, or instance"""
    logger.debug(f'Initializing backend: {backend} {cache_name}')

    # The 'cache_name' arg has a different purpose depending on the backend. If an equivalent
    # backend-specific keyword arg is specified, handle that here to avoid conflicts with the
    # 'cache_name' positional-or-keyword arg. In hindsight, a consistent positional-only or
    # keyword-only arg would have been better, but probably not worth a breaking change.
    cache_name_kwargs = [kwargs.pop(k) for k in CACHE_NAME_KWARGS if k in kwargs]
    cache_name = cache_name or cache_name_kwargs[0]

    # Already a backend instance
    if isinstance(backend, BaseCache):
        if cache_name:
            backend.cache_name = str(cache_name)
        return backend
    # If no backend is specified, use SQLite as default, unless the environment doesn't support it
    elif not backend:
        sqlite_supported = issubclass(BACKEND_CLASSES['sqlite'], BaseCache)
        backend = 'sqlite' if sqlite_supported else 'memory'

    # Get backend class by name
    backend = str(backend).lower()
    if backend not in BACKEND_CLASSES:
        raise ValueError(
            f'Invalid backend: {backend}. Provide a backend instance, or choose from one of the '
            f'following aliases: {list(BACKEND_CLASSES.keys())}'
        )
    return BACKEND_CLASSES[backend](cache_name, **kwargs)
