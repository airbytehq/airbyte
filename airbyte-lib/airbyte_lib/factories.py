# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from typing import Any, Dict, Optional

from airbyte_lib.cache import InMemoryCache
from airbyte_lib.executor import PathExecutor, VenvExecutor
from airbyte_lib.registry import get_connector_metadata
from airbyte_lib.source import Source


def get_in_memory_cache():
    return InMemoryCache()


def get_connector(name: str, version: str = "latest", config: Optional[Dict[str, Any]] = None, auto_install: bool = True):
    """
    Get a connector by name and version.
    :param name: connector name
    :param version: connector version - if not provided, the most recent version will be used
    :param config: connector config - if not provided, you need to set it later via the set_config method
    :param auto_install: whether to use a virtual environment to run the connector. If False, the connector is expected to be available on the path (e.g. installed via pip). If True, the connector will be installed automatically in a virtual environment.
    """
    metadata = get_connector_metadata(name)
    return Source(VenvExecutor(metadata, version) if auto_install else PathExecutor(metadata, version), name, config)
