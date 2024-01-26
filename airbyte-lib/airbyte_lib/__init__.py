"""AirbyteLib brings Airbyte ELT to every Python developer."""
from __future__ import annotations

from airbyte_lib._factories.cache_factories import get_default_cache, new_local_cache
from airbyte_lib._factories.connector_factories import get_connector
from airbyte_lib.caches import DuckDBCache, DuckDBCacheConfig
from airbyte_lib.datasets import CachedDataset
from airbyte_lib.results import ReadResult
from airbyte_lib.source import Source


__all__ = [
    "CachedDataset",
    "DuckDBCache",
    "DuckDBCacheConfig",
    "get_connector",
    "get_default_cache",
    "new_local_cache",
    "ReadResult",
    "Source",
]
