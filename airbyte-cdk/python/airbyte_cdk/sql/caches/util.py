# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Utility functions for working with caches."""

from __future__ import annotations

from pathlib import Path

import ulid

from airbyte_cdk.sql import exceptions as exc
from airbyte_cdk.sql.caches.duckdb import DuckDBCache


# Google drive constants:

_MY_DRIVE = "MyDrive"
"""The default name of the user's personal Google Drive."""

_GOOGLE_DRIVE_DEFAULT_MOUNT_PATH = "/content/drive"
"""The recommended path to mount Google Drive to."""


# Utility functions:


def get_default_cache() -> DuckDBCache:
    """Get a local cache for storing data, using the default database path.

    Cache files are stored in the `.cache` directory, relative to the current
    working directory.
    """
    cache_dir = Path("./.cache/default_cache")
    return DuckDBCache(
        db_path=cache_dir / "default_cache.duckdb",
        cache_dir=cache_dir,
    )


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
            raise exc.AirbyteInputError(
                message="Cache name cannot contain spaces.",
                input_value=cache_name,
            )

        if not cache_name.replace("_", "").isalnum():
            raise exc.AirbyteInputError(
                message="Cache name can only contain alphanumeric characters and underscores.",
                input_value=cache_name,
            )

    cache_name = cache_name or str(ulid.ULID())
    cache_dir = cache_dir or Path(f"./.cache/{cache_name}")
    if not isinstance(cache_dir, Path):
        cache_dir = Path(cache_dir)

    return DuckDBCache(
        db_path=cache_dir / f"db_{cache_name}.duckdb",
        cache_dir=cache_dir,
        cleanup=cleanup,
    )


def get_colab_cache(
    cache_name: str = "default_cache",
    sub_dir: str = "Airbyte/cache",
    schema_name: str = "main",
    table_prefix: str | None = "",
    drive_name: str = _MY_DRIVE,
    mount_path: str = _GOOGLE_DRIVE_DEFAULT_MOUNT_PATH,
) -> DuckDBCache:
    """Get a local cache for storing data, using the default database path.

    Unlike the default `DuckDBCache`, this implementation will easily persist data across multiple
    Colab sessions.

    Please note that Google Colab may prompt you to authenticate with your Google account to access
    your Google Drive. When prompted, click the link and follow the instructions.

    Colab will require access to read and write files in your Google Drive, so please be sure to
    grant the necessary permissions when prompted.

    All arguments are optional and have default values that are suitable for most use cases.

    Args:
        cache_name: The name to use for the cache. Defaults to "colab_cache". Override this if you
            want to use a different database for different projects.
        sub_dir: The subdirectory to store the cache in. Defaults to "Airbyte/cache". Override this
            if you want to store the cache in a different subdirectory than the default.
        schema_name: The name of the schema to write to. Defaults to "main". Override this if you
            want to write to a different schema.
        table_prefix: The prefix to use for all tables in the cache. Defaults to "". Override this
            if you want to use a different prefix for all tables.
        drive_name: The name of the Google Drive to use. Defaults to "MyDrive". Override this if you
            want to store data in a shared drive instead of your personal drive.
        mount_path: The path to mount Google Drive to. Defaults to "/content/drive". Override this
            if you want to mount Google Drive to a different path (not recommended).

    ## Usage Examples

    The default `get_colab_cache` arguments are suitable for most use cases:

    ```python
    from airbyte.caches.colab import get_colab_cache

    colab_cache = get_colab_cache()
    ```

    Or you can call `get_colab_cache` with custom arguments:

    ```python
    custom_cache = get_colab_cache(
        cache_name="my_custom_cache",
        sub_dir="Airbyte/custom_cache",
        drive_name="My Company Drive",
    )
    ```
    """
    try:
        from google.colab import drive  # noqa: PLC0415 # type: ignore[reportMissingImports]
    except ImportError:
        drive = None
        msg = (
            "The `google.colab` interface is only available in Google Colab. "
            "Please run this code in a Google Colab notebook."
        )
        raise ImportError(msg) from None

    drive.mount(mount_path)
    drive_root = (
        Path(mount_path) / drive_name
        if drive_name == _MY_DRIVE
        else Path(mount_path) / "Shareddrives" / drive_name
    )

    cache_dir = drive_root / sub_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    db_file_path = cache_dir / f"{cache_name}.duckdb"

    print(f"Using persistent Airbyte cache in Google Drive: `{db_file_path}`.")
    return DuckDBCache(
        db_path=db_file_path,
        cache_dir=cache_dir,
        schema_name=schema_name,
        table_prefix=table_prefix,
    )
