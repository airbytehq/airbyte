# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from typing import Any, Dict, Generic, Optional, TypeVar

from airbyte_lib.cache import Cache, InMemoryCache
from airbyte_lib.connection import Connection, SyncResult
from airbyte_lib.executor import VenvExecutor
from airbyte_lib.registry import get_connector_metadata
from airbyte_lib.source import Source

TCache = TypeVar("TCache", bound=Cache)


def get_in_memory_cache():
    return InMemoryCache()


def get_connector(name: str, version: str = "latest", config: Optional[Dict[str, Any]] = None):
    metadata = get_connector_metadata(name)
    return Source(VenvExecutor(metadata, version), name, config)


def sync(connector: Source, store: TCache) -> SyncResult[TCache]:
    return create_connection(connector, store).sync()


def create_connection(source: Source, cache: TCache) -> Connection[TCache]:
    return Connection(source, cache)
