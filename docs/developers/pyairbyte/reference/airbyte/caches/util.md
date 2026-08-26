---
id: airbyte-caches-util
title: airbyte.caches.util
---

Module airbyte.caches.util
==========================
Utility functions for working with caches.

Functions
---------

`get_colab_cache(cache_name: str = 'default_cache', sub_dir: str = 'Airbyte/cache', schema_name: str = 'main', table_prefix: str | None = '', drive_name: str = 'MyDrive', mount_path: str = '/content/drive') ‑> airbyte.caches.duckdb.DuckDBCache`
:   Get a local cache for storing data, using the default database path.
    
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

`get_default_cache() ‑> airbyte.caches.duckdb.DuckDBCache`
:   Get a local cache for storing data, using the default database path.
    
    Cache files are stored in the `.cache` directory, relative to the current
    working directory.

`new_local_cache(cache_name: str | None = None, cache_dir: str | Path | None = None, *, cleanup: bool = True) ‑> airbyte.caches.duckdb.DuckDBCache`
:   Get a local cache for storing data, using a name string to seed the path.
    
    Args:
        cache_name: Name to use for the cache. Defaults to None.
        cache_dir: Root directory to store the cache in. Defaults to None.
        cleanup: Whether to clean up temporary files. Defaults to True.
    
    Cache files are stored in the `.cache` directory, relative to the current
    working directory.