# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from typing import Any, Dict, Optional, TypeVar

from airbyte_lib.cache import Cache, InMemoryCache
from airbyte_lib.connection import Connection, SyncResult
from airbyte_lib.executor import DockerExecutor, PathExecutor, VenvExecutor
from airbyte_lib.registry import get_connector_metadata
from airbyte_lib.source import Source

TCache = TypeVar("TCache", bound=Cache)


def get_in_memory_cache():
    return InMemoryCache()


def get_connector(
    name: str, version: str = "latest", config: Optional[Dict[str, Any]] = None, auto_install: bool = True, use_docker: bool = False
) -> Source:
    """
    Get a connector by name and version.
    :param name: connector name
    :param version: connector version - if not provided, the most recent version will be used
    :param config: connector config - if not provided, you need to set it later via the set_config method
    :param auto_install: whether to use a virtual environment to run the connector. If False, the connector is expected to be available already (e.g. installed via pip). If True, the connector will be installed automatically (either in a virtual environment if docker is not available or by pulling the docker image).
    :param use_docker: Whether to use docker to run the connector. If False, the connector is expected to be available on the path (e.g. installed via pip). If True, the connector will be run in a docker container.
    """
    metadata = get_connector_metadata(name)
    if use_docker:
        return Source(DockerExecutor(metadata, version), name, config)
    elif auto_install:
        return Source(VenvExecutor(metadata, version), name, config)
    else:
        return Source(PathExecutor(metadata, version), name, config)


def sync(connector: Source, store: TCache) -> SyncResult[TCache]:
    return create_connection(connector, store).sync()


def create_connection(source: Source, cache: TCache) -> Connection[TCache]:
    return Connection(source, cache)
