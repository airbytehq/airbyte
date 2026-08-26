---
id: airbyte-destinations-index
title: airbyte.destinations.index
---

Module airbyte.destinations
===========================
Destinations module.

This module contains classes and methods for interacting with Airbyte destinations. You can use this
module to create custom destinations, or to interact with existing destinations.

## Getting Started

To get started with destinations, you can use the `get_destination()` method to create a destination
object. This method takes a destination name and configuration, and returns a destination object
that you can use to write data to the destination.

```python
import airbyte as ab

my_destination = ab.get_destination(
    "destination-foo",
    config={"api_key": "my_api_key"},
    docker_image=True,
)
```

## Writing Data to a Destination

To write data to a destination, you can use the `Destination.write()` method. This method
takes either a `airbyte.Source` or `airbyte.ReadResult` object.

## Writing to a destination from a source

To write directly from a source, simply pass the source object to the `Destination.write()` method:

```python
my_source = get_source(...)
my_destination = get_destination(...)
my_destination.write(source_faker)
```

## Writing from a read result:

To write from a read result, you can use the following pattern. First, read data from the source,
then write the data to the destination, using the `ReadResult` object as a buffer between the source
and destination:

```python
# First read data from the source:
my_source = get_source(...)
read_result = my_source.read(...)

# Optionally, you can validate data before writing it:
# ...misc validation code here...

# Then write the data to the destination:
my_destination.write(read_result)
```

## Using Docker and Python-based Connectors

By default, the `get_destination()` method will look for a Python-based connector. If you want to
use a Docker-based connector, you can set the `docker_image` parameter to `True`:

```python
my_destination = ab.get_destination(
    "destination-foo",
    config={"api_key": "my_api_key"},
    docker_image=True,
)
```

**Note:** Unlike source connectors, most destination connectors are written in Java, and for this
reason are only available as Docker-based connectors. If you need to load to a SQL database and your
runtime does not support docker, you may want to use the `airbyte.caches` module to load data to
a SQL cache. Caches are mostly identical to destinations in behavior, and are implemented internally
to PyAirbyte so they can run anywhere that PyAirbyte can run.

Sub-modules
-----------
* airbyte.destinations.base
* airbyte.destinations.util

Functions
---------

`get_destination(name: str, config: dict[str, Any] | None = None, *, config_change_callback: ConfigChangeCallback | None = None, version: str | None = None, use_python: bool | Path | str | None = None, pip_url: str | None = None, local_executable: Path | str | None = None, docker_image: str | bool | None = None, use_host_network: bool = False, install_if_missing: bool = True, install_root: Path | None = None, no_executor: bool = False) ‑> Destination`
:   Get a connector by name and version.
    
    Args:
        name: connector name
        config: connector config - if not provided, you need to set it later via the set_config
            method.
        config_change_callback: callback function to be called when the connector config changes.
        streams: list of stream names to select for reading. If set to "*", all streams will be
            selected. If not provided, you can set it later via the `select_streams()` or
            `select_all_streams()` method.
        version: connector version - if not provided, the currently installed version will be used.
            If no version is installed, the latest available version will be used. The version can
            also be set to "latest" to force the use of the latest available version.
        use_python: (Optional.) Python interpreter specification:
            - True: Use current Python interpreter. (Inferred if `pip_url` is set.)
            - False: Use Docker instead.
            - Path: Use interpreter at this path.
            - str: Use specific Python version. E.g. "3.11" or "3.11.10". If the version is not yet
                installed, it will be installed by uv. (This generally adds less than 3 seconds
                to install times.)
        pip_url: connector pip URL - if not provided, the pip url will be inferred from the
            connector name.
        local_executable: If set, the connector will be assumed to already be installed and will be
            executed using this path or executable name. Otherwise, the connector will be installed
            automatically in a virtual environment.
        docker_image: If set, the connector will be executed using Docker. You can specify `True`
            to use the default image for the connector, or you can specify a custom image name.
            If `version` is specified and your image name does not already contain a tag
            (e.g. `my-image:latest`), the version will be appended as a tag (e.g. `my-image:0.1.0`).
        use_host_network: If set, along with docker_image, the connector will be executed using
            the host network. This is useful for connectors that need to access resources on
            the host machine, such as a local database. This parameter is ignored when
            `docker_image` is not set.
        install_if_missing: Whether to install the connector if it is not available locally. This
            parameter is ignored when local_executable is set.
        install_root: (Optional.) The root directory where the virtual environment will be
            created. If not provided, the current working directory will be used.
        no_executor: If True, use NoOpExecutor which fetches specs from the registry without
            local installation. This is useful for scenarios where you need to validate
            configurations but don't need to run the connector locally (e.g., deploying to Cloud).

`get_noop_destination(*, install_if_missing: bool = True) ‑> airbyte.destinations.base.Destination`
:   Get a devnull (no-op) destination.
    
    This is useful for performance benchmarking of sources, without
    adding the overhead of writing data to a real destination.

Classes
-------

`Destination(executor: Executor, name: str, config: dict[str, Any] | None = None, *, config_change_callback: ConfigChangeCallback | None = None, validate: bool = False)`
:   A class representing a destination that can be called.
    
    Initialize the source.
    
    If config is provided, it will be validated against the spec if validate is True.

    ### Ancestors (in MRO)

    * airbyte._connector_base.ConnectorBase
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Class variables

    `connector_type: Literal['destination', 'source']`
    :

    ### Methods

    `write(self, source_data: Source | ReadResult, *, streams: "list[str] | Literal['*'] | None" = None, cache: CacheBase | Literal[False] | None = None, state_cache: CacheBase | Literal[False] | None = None, write_strategy: WriteStrategy = WriteStrategy.AUTO, force_full_refresh: bool = False) ‑> WriteResult`
    :   Write data from source connector or already cached source data.
        
        Caching is enabled by default, unless explicitly disabled.
        
        Args:
            source_data: The source data to write. Can be a `Source` or a `ReadResult` object.
            streams: The streams to write to the destination. If omitted or if "*" is provided,
                all streams will be written. If `source_data` is a source, then streams must be
                selected here or on the source. If both are specified, this setting will override
                the stream selection on the source.
            cache: The cache to use for reading source_data. If `None`, no cache will be used. If
                False, the cache will be disabled. This must be `None` if `source_data` is already
                a `Cache` object.
            state_cache: A cache to use for storing incremental state. You do not need to set this
                if `cache` is specified or if `source_data` is a `Cache` object. Set to `False` to
                disable state management.
            write_strategy: The strategy to use for writing source_data. If `AUTO`, the connector
                will decide the best strategy to use.
            force_full_refresh: Whether to force a full refresh of the source_data. If `True`, any
                existing state will be ignored and all source data will be reloaded.
        
        For incremental syncs, `cache` or `state_cache` will be checked for matching state values.
        If the cache has tracked state, this will be used for the sync. Otherwise, if there is
        a known destination state, the destination-specific state will be used. If neither are
        available, a full refresh will be performed.