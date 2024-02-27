"""Base module for all caches."""
from __future__ import annotations

from airbyte_lib.caches.base import SQLCacheBase
from airbyte_lib.caches.duckdb import DuckDBCache, DuckDBCacheConfig
from airbyte_lib.caches.postgres import PostgresCache, PostgresCacheConfig
from airbyte_lib.caches.snowflake import SnowflakeCacheConfig, SnowflakeSQLCache


# We export these classes for easy access: `airbyte_lib.caches...`
__all__ = [
    "DuckDBCache",
    "DuckDBCacheConfig",
    "PostgresCache",
    "PostgresCacheConfig",
    "SQLCacheBase",
    "SnowflakeCacheConfig",
    "SnowflakeSQLCache",
]
