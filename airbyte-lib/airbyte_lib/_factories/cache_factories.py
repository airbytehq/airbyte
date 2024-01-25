# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from pathlib import Path

import ulid

from airbyte_lib import exceptions as exc
from airbyte_lib.caches.duckdb import DuckDBCache, DuckDBCacheConfig


def get_default_cache() -> DuckDBCache:
    """Get a local cache for storing data, using the default database path.

    Cache files are stored in the `.cache` directory, relative to the current
    working directory.
    """
    config = DuckDBCacheConfig(
        db_path="./.cache/default_cache_db.duckdb",
    )
    return DuckDBCache(config=config)


def new_local_cache(
    cache_name: str | None = None,
    cache_dir: str | Path | None = None,
    *,
    cleanup: bool = True,
) -> DuckDBCache:
    """Get a local cache for storing data, using a name string to seed the path.

    Args:
        cache_name: Name to use for the cache. Defaults to None.
        cache_dir: Root directory to store the cache in. Defaults to None.
        cleanup: Whether to clean up temporary files. Defaults to True.

    Cache files are stored in the `.cache` directory, relative to the current
    working directory.
    """
    if cache_name:
        if " " in cache_name:
            raise exc.AirbyteLibInputError(
                message="Cache name cannot contain spaces.",
                input_value=cache_name,
            )

        if not cache_name.replace("_", "").isalnum():
            raise exc.AirbyteLibInputError(
                message="Cache name can only contain alphanumeric characters and underscores.",
                input_value=cache_name,
            )

    cache_name = cache_name or str(ulid.ULID())
    cache_dir = cache_dir or Path(f"./.cache/{cache_name}")
    if not isinstance(cache_dir, Path):
        cache_dir = Path(cache_dir)

    config = DuckDBCacheConfig(
        db_path=cache_dir / f"db_{cache_name}.duckdb",
        cache_dir=cache_dir,
        cleanup=cleanup,
    )
    return DuckDBCache(config=config)
