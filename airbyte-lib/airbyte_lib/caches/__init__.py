"""Base module for all caches."""

from airbyte_lib.caches.base import SQLCacheBase
from airbyte_lib.types import SQLTypeConverter
from airbyte_lib.caches.duckdb import DuckDBCache, DuckDBCacheConfig
from airbyte_lib.caches.memory import InMemoryCache, InMemoryCacheConfig


# We export these classes for easy access: `airbyte_lib.caches...`
__all__ = [
    "DuckDBCache",
    "DuckDBCacheConfig",
    "InMemoryCache",
    "InMemoryCacheConfig",
    "SQLCacheBase",
    "SQLTypeConverter",
]
