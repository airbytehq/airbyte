"""Base module for all caches."""

from airbyte_lib.caches.base import SQLCacheBase
from airbyte_lib.caches.duckdb import DuckDBCache, DuckDBCacheConfig
from airbyte_lib.caches.postgres import PostgresCache, PostgresCacheConfig


# We export these classes for easy access: `airbyte_lib.caches...`
__all__ = [
    "DuckDBCache",
    "DuckDBCacheConfig",
    "PostgresCache",
    "PostgresCacheConfig",
    "SQLCacheBase",
]
