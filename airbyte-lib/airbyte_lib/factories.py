# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from typing import Any, Dict, Optional

from airbyte_protocol.models import ConfiguredAirbyteCatalog
import ulid
from airbyte_lib.caches.duckdb import DuckDBCache, DuckDBCacheConfig

from airbyte_lib.executor import PathExecutor, VenvExecutor
from airbyte_lib.registry import get_connector_metadata
from airbyte_lib.source import Source


def get_default_cache(source_catalog: ConfiguredAirbyteCatalog) -> DuckDBCache:
    """Get a local cache for storing data, using the default database path.

    Cache files are stored in the `.cache` directory, relative to the current
    working directory.
    """
    config = DuckDBCacheConfig(
        db_path="./.cache/default_cache_db.duckdb",
    )
    return DuckDBCache(
        config=config,
        source_catalog=source_catalog,
    )


def new_local_cache(
    cache_name: str | None = None,
    *,
    source_catalog: ConfiguredAirbyteCatalog,
) -> DuckDBCache:
    """Get a local cache for storing data, using a string to determine the.

    Cache files are stored in the `.cache` directory, relative to the current
    working directory.
    """
    cache_name = cache_name or str(ulid.ULID())
    config = DuckDBCacheConfig(
        db_path=f"./.cache/db_{cache_name}.duckdb",
    )
    return DuckDBCache(
        config=config,
        source_catalog=source_catalog,
    )


def get_connector(
    name: str,
    version: str | None = None,
    pip_url: str | None = None,
    config: dict[str, Any] | None = None,
    use_local_install: bool = False,
    install_if_missing: bool = False,
):
    """
    Get a connector by name and version.
    :param name: connector name
    :param version: connector version - if not provided, the most recent version will be used.
    :param pip_url: connector pip URL - if not provided, the pip url will be inferred from the connector name.
    :param config: connector config - if not provided, you need to set it later via the set_config method.
    :param use_local_install: whether to use a virtual environment to run the connector. If True, the connector is expected to be available on the path (e.g. installed via pip). If False, the connector will be installed automatically in a virtual environment.
    :param install_if_missing: whether to install the connector if it is not available locally. This parameter is ignored if use_local_install is True.
    """
    metadata = get_connector_metadata(name)
    if use_local_install:
        if pip_url:
            raise ValueError(
                "Param 'pip_url' is not supported when 'use_local_install' is True"
            )
        if version:
            raise ValueError(
                "Param 'version' is not supported when 'use_local_install' is True"
            )
        executor = PathExecutor(
            metadata=metadata,
            target_version=version,
        )

    else:
        executor = VenvExecutor(
            metadata=metadata,
            target_version=version,
            install_if_missing=install_if_missing,
            pip_url=pip_url,
        )
    return Source(
        executor=executor,
        name=name,
        config=config,
    )
