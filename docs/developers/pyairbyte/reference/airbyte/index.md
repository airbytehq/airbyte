---
id: airbyte-index
title: airbyte.index
---

Module airbyte
==============
***PyAirbyte brings the power of Airbyte to every Python developer.***

[![PyPI version](https://badge.fury.io/py/airbyte.svg)](https://badge.fury.io/py/airbyte)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/airbyte)](https://pypi.org/project/airbyte/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/airbyte)](https://pypi.org/project/airbyte/)
[![Star on GitHub](https://img.shields.io/github/stars/airbytehq/pyairbyte.svg?style=social&label=★%20on%20GitHub)](https://github.com/airbytehq/pyairbyte)

# Getting Started

## Reading Data

You can connect to any of [hundreds of sources](https://docs.airbyte.com/integrations/sources/)
using the `get_source` method. You can then read data from sources using `Source.read` method.

```python
from airbyte import get_source

source = get_source(
    "source-faker",
    config={},
)
read_result = source.read()

for record in read_result["users"].records:
    print(record)
```

For more information, see the `airbyte.sources` module.

## Writing to SQL Caches

Data can be written to caches using a number of SQL-based cache implementations, including
Postgres, BigQuery, Snowflake, DuckDB, and MotherDuck. If you do not specify a cache, PyAirbyte
will automatically use a local DuckDB cache by default.

For more information, see the `airbyte.caches` module.

## Writing to Destination Connectors

Data can be written to destinations using the `Destination.write` method. You can connect to
destinations using the `get_destination` method. PyAirbyte supports all Airbyte destinations, but
Docker is required on your machine in order to run Java-based destinations.

**Note:** When loading to a SQL database, we recommend using SQL cache (where available,
[see above](#writing-to-sql-caches)) instead of a destination connector. This is because SQL caches
are Python-native and therefor more portable when run from different Python-based environments which
might not have Docker container support. Destinations in PyAirbyte are uniquely suited for loading
to non-SQL platforms such as vector stores and other reverse ETL-type use cases.

For more information, see the `airbyte.destinations` module and the full list of destination
connectors [here](https://docs.airbyte.com/integrations/destinations/).

# PyAirbyte API

## Importing as `ab`

Most examples in the PyAirbyte documentation use the `import airbyte as ab` convention. The `ab`
alias is recommended, making code more concise and readable. When getting started, this
also saves you from digging in submodules to find the classes and functions you need, since
frequently-used classes and functions are available at the top level of the `airbyte` module.

## Navigating the API

While many PyAirbyte classes and functions are available at the top level of the `airbyte` module,
you can also import classes and functions from submodules directly. For example, while you can
import the `Source` class from `airbyte`, you can also import it from the `sources` submodule like
this:

```python
from airbyte.sources import Source
```

Whether you import from the top level or from a submodule, the classes and functions are the same.
We expect that most users will import from the top level when getting started, and then import from
submodules when they are deploying more complex implementations.

For quick reference, top-Level modules are listed in the left sidebar of this page.

# Other Resources

- [PyAirbyte GitHub Readme](https://github.com/airbytehq/pyairbyte)
- [PyAirbyte Issue Tracker](https://github.com/airbytehq/pyairbyte/issues)
- [Frequently Asked Questions](https://github.com/airbytehq/PyAirbyte/blob/main/docs/faq.md)
- [PyAirbyte Contributors Guide](https://github.com/airbytehq/PyAirbyte/blob/main/docs/CONTRIBUTING.md)
- [GitHub Releases](https://github.com/airbytehq/PyAirbyte/releases)

----------------------

# API Reference

Below is a list of all classes, functions, and modules available in the top-level `airbyte`
module. (This is a long list!) If you are just starting out, we recommend beginning by selecting a
submodule to navigate to from the left sidebar or from the list below:

Each module
has its own documentation and code samples related to effectively using the related capabilities.

- **`airbyte.cloud`** - Working with Airbyte Cloud, including running jobs remotely.
- **`airbyte.caches`** - Working with caches, including how to inspect a cache and get data from it.
- **`airbyte.datasets`** - Working with datasets, including how to read from datasets and convert to
    other formats, such as Pandas, Arrow, and LLM Document formats.
- **`airbyte.destinations`** - Working with destinations, including how to write to Airbyte
    destinations connectors.
- **`airbyte.documents`** - Working with LLM documents, including how to convert records into
    document formats, for instance, when working with AI libraries like LangChain.
- **`airbyte.exceptions`** - Definitions of all exception and warning classes used in PyAirbyte.
- **`airbyte.experimental`** - Experimental features and utilities that do not yet have a stable
    API.
- **`airbyte.logs`** - Logging functionality and configuration.
- **`airbyte.records`** - Internal record handling classes.
- **`airbyte.results`** - Documents the classes returned when working with results from
    `Source.read` and `Destination.write`
- **`airbyte.secrets`** - Tools for managing secrets in PyAirbyte.
- **`airbyte.sources`** - Tools for creating and reading from Airbyte sources. This includes
    `airbyte.source.get_source` to declare a source, `airbyte.source.Source.read` for reading data,
    and `airbyte.source.Source.get_records()` to peek at records without caching or writing them
    directly.

----------------------

Sub-modules
-----------
* airbyte.caches
* airbyte.callbacks
* airbyte.cli
* airbyte.cloud
* airbyte.constants
* airbyte.datasets
* airbyte.destinations
* airbyte.documents
* airbyte.exceptions
* airbyte.experimental
* airbyte.logs
* airbyte.mcp
* airbyte.progress
* airbyte.records
* airbyte.registry
* airbyte.results
* airbyte.secrets
* airbyte.shared
* airbyte.sources
* airbyte.strategies
* airbyte.types
* airbyte.validate
* airbyte.version

Functions
---------

`get_available_connectors(install_type: InstallType | str | None = InstallType.INSTALLABLE) ‑> list[str]`
:   Return a list of all available connectors.
    
    Connectors will be returned in alphabetical order, with the standard prefix "source-".
    
    Args:
        install_type: The type of installation for the connector.
            Defaults to `InstallType.INSTALLABLE`.

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

`get_secret(secret_name: str, /, *, sources: list[SecretManager | SecretSourceEnum] | None = None, default: str | SecretString | None = None, allow_prompt: bool = True, **kwargs: dict[str, Any]) ‑> airbyte.secrets.base.SecretString`
:   Get a secret from the environment.
    
    The optional `sources` argument of enum type `SecretSourceEnum` or list of `SecretSourceEnum`
    options. If left blank, all available sources will be checked. If a list of `SecretSourceEnum`
    entries is passed, then the sources will be checked using the provided ordering.
    
    If `allow_prompt` is `True` or if SecretSourceEnum.PROMPT is declared in the `source` arg, then
    the user will be prompted to enter the secret if it is not found in any of the other sources.
    
    Raises:
        PyAirbyteSecretNotFoundError: If the secret is not found in any of the configured sources,
            and if no default value is provided.
        PyAirbyteInputError: If an invalid source name is provided in the `sources` argument.

`get_source(name: str, config: dict[str, Any] | None = None, *, config_change_callback: ConfigChangeCallback | None = None, streams: str | list[str] | None = None, version: str | None = None, use_python: bool | Path | str | None = None, pip_url: str | None = None, local_executable: Path | str | None = None, docker_image: bool | str | None = None, use_host_network: bool = False, source_manifest: bool | dict | Path | str | None = None, install_if_missing: bool = True, install_root: Path | None = None, no_executor: bool = False) ‑> Source`
:   Get a connector by name and version.
    
    If an explicit install or execution method is requested (e.g. `local_executable`,
    `docker_image`, `pip_url`, `source_manifest`), the connector will be executed using this method.
    
    Otherwise, an appropriate method will be selected based on the available connector metadata:
    1. If the connector is registered and has a YAML source manifest is available, the YAML manifest
       will be downloaded and used to to execute the connector.
    2. Else, if the connector is registered and has a PyPI package, it will be installed via pip.
    3. Else, if the connector is registered and has a Docker image, and if Docker is available, it
       will be executed using Docker.
    
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
        source_manifest: If set, the connector will be executed based on a declarative YAML
            source definition. This input can be `True` to attempt to auto-download a YAML spec,
            `dict` to accept a Python dictionary as the manifest, `Path` to pull a manifest from
            the local file system, or `str` to pull the definition from a web URL.
        install_if_missing: Whether to install the connector if it is not available locally. This
            parameter is ignored when `local_executable` or `source_manifest` are set.
        install_root: (Optional.) The root directory where the virtual environment will be
            created. If not provided, the current working directory will be used.
        no_executor: If True, use NoOpExecutor which fetches specs from the registry without
            local installation. This is useful for scenarios where you need to validate
            configurations but don't need to run the connector locally (e.g., deploying to Cloud).

`new_local_cache(cache_name: str | None = None, cache_dir: str | Path | None = None, *, cleanup: bool = True) ‑> airbyte.caches.duckdb.DuckDBCache`
:   Get a local cache for storing data, using a name string to seed the path.
    
    Args:
        cache_name: Name to use for the cache. Defaults to None.
        cache_dir: Root directory to store the cache in. Defaults to None.
        cleanup: Whether to clean up temporary files. Defaults to True.
    
    Cache files are stored in the `.cache` directory, relative to the current
    working directory.

Classes
-------

`BigQueryCache(**data: Any)`
:   The BigQuery cache implementation.
    
    Initialize the cache and backends.

    ### Ancestors (in MRO)

    * airbyte._processors.sql.bigquery.BigQueryConfig
    * airbyte.caches.base.CacheBase
    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Class variables

    `model_config`
    :

    `paired_destination_config_class: ClassVar[type | None]`
    :   DestinationBigquery(dataset_id: 'str', dataset_location: 'DatasetLocation', project_id: 'str', cdc_deletion_mode: 'Optional[CDCDeletionMode]' = &lt;CDCDeletionMode.HARD_DELETE: 'Hard delete'&gt;, credentials_json: 'Optional[str]' = None, DESTINATION_TYPE: 'Final[Bigquery]' = &lt;Bigquery.BIGQUERY: 'bigquery'&gt;, disable_type_dedupe: 'Optional[bool]' = False, loading_method: 'Optional[LoadingMethod]' = None, raw_data_dataset: 'Optional[str]' = None)

    `paired_destination_name: ClassVar[str | None]`
    :

    ### Methods

    `get_arrow_dataset(self, stream_name: str, *, max_chunk_size: int = 100000) ‑> NoReturn`
    :   Raises NotImplementedError; BigQuery doesn't support `pd.read_sql_table`.
        
        See: https://github.com/airbytehq/PyAirbyte/issues/165

`CachedDataset(cache: CacheBase, stream_name: str, stream_configuration: ConfiguredAirbyteStream | Literal[False] | None = None)`
:   A dataset backed by a SQL table cache.
    
    Because this dataset includes all records from the underlying table, we also expose the
    underlying table as a SQLAlchemy Table object.
    
    We construct the query statement by selecting all columns from the table.
    
    This prevents the need to scan the table schema to construct the query statement.
    
    If stream_configuration is None, we attempt to retrieve the stream configuration from the
    cache processor. This is useful when constructing a dataset from a CachedDataset object,
    which already has the stream configuration.
    
    If stream_configuration is set to False, we skip the stream configuration retrieval.

    ### Ancestors (in MRO)

    * airbyte.datasets._sql.SQLDataset
    * airbyte.datasets._base.DatasetBase
    * abc.ABC

    ### Methods

    `to_arrow(self, *, max_chunk_size: int = 100000) ‑> Dataset`
    :   Return an Arrow Dataset containing the data from the specified stream.
        
        Args:
            stream_name (str): Name of the stream to retrieve data from.
            max_chunk_size (int): max number of records to include in each batch of pyarrow dataset.
        
        Returns:
            pa.dataset.Dataset: Arrow Dataset containing the stream's data.

    `to_pandas(self) ‑> DataFrame`
    :   Return the underlying dataset data as a pandas DataFrame.

    `to_sql_table(self) ‑> Table`
    :   Return the underlying SQL table as a SQLAlchemy Table object.

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

`DuckDBCache(**data: Any)`
:   A DuckDB cache.
    
    Initialize the cache and backends.

    ### Ancestors (in MRO)

    * airbyte._processors.sql.duckdb.DuckDBConfig
    * airbyte.caches.base.CacheBase
    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Descendants

    * airbyte.caches.motherduck.MotherDuckCache

    ### Class variables

    `model_config`
    :

    `paired_destination_config_class: ClassVar[type | None]`
    :   DestinationDuckdb(destination_path: 'str', DESTINATION_TYPE: 'Final[Duckdb]' = &lt;Duckdb.DUCKDB: 'duckdb'&gt;, motherduck_api_key: 'Optional[str]' = None, schema: 'Optional[str]' = None)

    `paired_destination_name: ClassVar[str | None]`
    :

`ReadResult(*, source_name: str, processed_streams: list[str], cache: CacheBase, progress_tracker: ProgressTracker)`
:   The result of a read operation.
    
    This class is used to return information about the read operation, such as the number of
    records read. It should not be created directly, but instead returned by the write method
    of a destination.
    
    Initialize a read result.
    
    This class should not be created directly. Instead, it should be returned by the `read`
    method of the `Source` class.

    ### Ancestors (in MRO)

    * collections.abc.Mapping
    * collections.abc.Collection
    * collections.abc.Sized
    * collections.abc.Iterable
    * collections.abc.Container

    ### Instance variables

    `cache: CacheBase`
    :   Return the cache object.

    `processed_records: int`
    :   The total number of records read from the source.

    `streams: Mapping[str, CachedDataset]`
    :   Return a mapping of stream names to cached datasets.

    ### Methods

    `get_sql_engine(self) ‑> Engine`
    :   Return the SQL engine used by the cache.

`SecretSourceEnum(*args, **kwds)`
:   Enumeration of secret sources supported by PyAirbyte.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `DOTENV`
    :

    `ENV`
    :

    `GOOGLE_COLAB`
    :

    `GOOGLE_GSM`
    :

    `PROMPT`
    :

`Source(executor: Executor, name: str, config: dict[str, Any] | None = None, *, config_change_callback: ConfigChangeCallback | None = None, streams: str | list[str] | None = None, validate: bool = False, cursor_key_overrides: dict[str, str] | None = None, primary_key_overrides: dict[str, str | list[str]] | None = None)`
:   A class representing a source that can be called.
    
    Initialize the source.
    
    If config is provided, it will be validated against the spec if validate is True.

    ### Ancestors (in MRO)

    * airbyte._connector_base.ConnectorBase
    * abc.ABC

    ### Class variables

    `connector_type: Literal['destination', 'source']`
    :

    ### Instance variables

    `config_spec: dict[str, Any]`
    :   Generate a configuration spec for this connector, as a JSON Schema definition.
        
        This function generates a JSON Schema dictionary with configuration specs for the
        current connector, as a dictionary.
        
        Returns:
            dict: The JSON Schema configuration spec as a dictionary.

    `configured_catalog: ConfiguredAirbyteCatalog`
    :   Get the configured catalog for the given streams.
        
        If the raw catalog is not yet known, we call discover to get it.
        
        If no specific streams are selected, we return a catalog that syncs all available streams.
        
        TODO: We should consider disabling by default the streams that the connector would
        disable by default. (For instance, streams that require a premium license are sometimes
        disabled by default within the connector.)

    `discovered_catalog: AirbyteCatalog`
    :   Get the raw catalog for the given streams.
        
        If the catalog is not yet known, we call discover to get it.

    `docs_url: str`
    :   Get the URL to the connector's documentation.

    ### Methods

    `get_available_streams(self) ‑> list[str]`
    :   Get the available streams from the spec.

    `get_configured_catalog(self, streams: "Literal['*'] | list[str] | None" = None, *, force_full_refresh: bool = False) ‑> airbyte_protocol.models.airbyte_protocol.ConfiguredAirbyteCatalog`
    :   Get a configured catalog for the given streams.
        
        If no streams are provided, the selected streams will be used. If no streams are selected,
        all available streams will be used.
        
        If '*' is provided, all available streams will be used.
        
        If force_full_refresh is True, streams will be configured with full_refresh sync mode
        when supported by the stream. Otherwise, incremental sync mode is used when supported.

    `get_documents(self, stream: str, title_property: str | None = None, content_properties: list[str] | None = None, metadata_properties: list[str] | None = None, *, render_metadata: bool = False) ‑> Iterable[Document]`
    :   Read a stream from the connector and return the records as documents.
        
        If metadata_properties is not set, all properties that are not content will be added to
        the metadata.
        
        If render_metadata is True, metadata will be rendered in the document, as well as the
        the main content.

    `get_records(self, stream: str, *, limit: int | None = None, stop_event: threading.Event | None = None, normalize_field_names: bool = False, prune_undeclared_fields: bool = True) ‑> airbyte.datasets._lazy.LazyDataset`
    :   Read a stream from the connector.
        
        Args:
            stream: The name of the stream to read.
            limit: The maximum number of records to read. If None, all records will be read.
            stop_event: If set, the event can be triggered by the caller to stop reading records
                and terminate the process.
            normalize_field_names: When `True`, field names will be normalized to lower case, with
                special characters removed. This matches the behavior of PyAirbyte caches and most
                Airbyte destinations.
            prune_undeclared_fields: When `True`, undeclared fields will be pruned from the records,
                which generally matches the behavior of PyAirbyte caches and most Airbyte
                destinations, specifically when you expect the catalog may be stale. You can disable
                this to keep all fields in the records.
        
        This involves the following steps:
        * Call discover to get the catalog
        * Generate a configured catalog that syncs the given stream in full_refresh mode
        * Write the configured catalog and the config to a temporary file
        * execute the connector with read --config &lt;config_file&gt; --catalog &lt;catalog_file&gt;
        * Listen to the messages and return the first AirbyteRecordMessages that come along.
        * Make sure the subprocess is killed when the function returns.

    `get_samples(self, streams: "list[str] | Literal['*'] | None" = None, *, limit: int = 5, on_error: "Literal['raise', 'ignore', 'log']" = 'raise') ‑> dict[str, InMemoryDataset | None]`
    :   Get a sample of records from the given streams.

    `get_selected_streams(self) ‑> list[str]`
    :   Get the selected streams.
        
        If no streams are selected, return an empty list.

    `get_stream_json_schema(self, stream_name: str) ‑> dict[str, typing.Any]`
    :   Return the JSON Schema spec for the specified stream name.

    `print_samples(self, streams: "list[str] | Literal['*'] | None" = None, *, limit: int = 5, on_error: "Literal['raise', 'ignore', 'log']" = 'log') ‑> None`
    :   Print a sample of records from the given streams.

    `read(self, cache: CacheBase | None = None, *, streams: str | list[str] | None = None, write_strategy: str | WriteStrategy = WriteStrategy.AUTO, force_full_refresh: bool = False, skip_validation: bool = False) ‑> ReadResult`
    :   Read from the connector and write to the cache.
        
        Args:
            cache: The cache to write to. If not set, a default cache will be used.
            streams: Optional if already set. A list of stream names to select for reading. If set
                to "*", all streams will be selected.
            write_strategy: The strategy to use when writing to the cache. If a string, it must be
                one of "append", "merge", "replace", or "auto". If a WriteStrategy, it must be one
                of WriteStrategy.APPEND, WriteStrategy.MERGE, WriteStrategy.REPLACE, or
                WriteStrategy.AUTO.
            force_full_refresh: If True, the source will operate in full refresh mode. Otherwise,
                streams will be read in incremental mode if supported by the connector. This option
                must be True when using the "replace" strategy.
            skip_validation: If True, PyAirbyte will not pre-validate the input configuration before
                running the connector. This can be helpful in debugging, when you want to send
                configurations to the connector that otherwise might be rejected by JSON Schema
                validation rules.

    `select_all_streams(self) ‑> None`
    :   Select all streams.
        
        This is a more streamlined equivalent to:
        > source.select_streams(source.get_available_streams()).

    `select_streams(self, streams: str | list[str]) ‑> None`
    :   Select the stream names that should be read from the connector.
        
        Args:
            streams: A list of stream names to select. If set to "*", all streams will be selected.
        
        Currently, if this is not set, all streams will be read.

    `set_config(self, config: dict[str, Any], *, validate: bool = True) ‑> None`
    :   Set the config for the connector.
        
        If validate is True, raise an exception if the config fails validation.
        
        If validate is False, validation will be deferred until check() or validate_config()
        is called.

    `set_cursor_key(self, stream_name: str, cursor_key: str) ‑> None`
    :   Set the cursor for a single stream.
        
        Note:
        - This does not unset previously set cursors.
        - The cursor key must be a single field name.
        - Not all streams support custom cursors. If a stream does not support custom cursors,
          the override may be ignored.
        - Stream names are case insensitive, while field names are case sensitive.
        - Stream names are not validated by PyAirbyte. If the stream name
          does not exist in the catalog, the override may be ignored.

    `set_cursor_keys(self, **kwargs: str) ‑> None`
    :   Override the cursor key for one or more streams.
        
        Usage:
            source.set_cursor_keys(
                stream1="cursor1",
                stream2="cursor2",
            )
        
        Note:
        - This does not unset previously set cursors.
        - The cursor key must be a single field name.
        - Not all streams support custom cursors. If a stream does not support custom cursors,
          the override may be ignored.
        - Stream names are case insensitive, while field names are case sensitive.
        - Stream names are not validated by PyAirbyte. If the stream name
          does not exist in the catalog, the override may be ignored.

    `set_primary_key(self, stream_name: str, primary_key: str | list[str]) ‑> None`
    :   Set the primary key for a single stream.
        
        Note:
        - This does not unset previously set primary keys.
        - The primary key must be a single field name or a list of field names.
        - Not all streams support overriding primary keys. If a stream does not support overriding
          primary keys, the override may be ignored.
        - Stream names are case insensitive, while field names are case sensitive.
        - Stream names are not validated by PyAirbyte. If the stream name
          does not exist in the catalog, the override may be ignored.

    `set_primary_keys(self, **kwargs: str | list[str]) ‑> None`
    :   Override the primary keys for one or more streams.
        
        This does not unset previously set primary keys.
        
        Usage:
            source.set_primary_keys(
                stream1="pk1",
                stream2=["pk1", "pk2"],
            )
        
        Note:
        - This does not unset previously set primary keys.
        - The primary key must be a single field name or a list of field names.
        - Not all streams support overriding primary keys. If a stream does not support overriding
          primary keys, the override may be ignored.
        - Stream names are case insensitive, while field names are case sensitive.
        - Stream names are not validated by PyAirbyte. If the stream name
          does not exist in the catalog, the override may be ignored.

    `set_streams(self, streams: list[str]) ‑> None`
    :   Deprecated. See select_streams().

`StreamRecord(from_dict: dict, *, stream_record_handler: StreamRecordHandler, with_internal_columns: bool = True, extracted_at: datetime | None = None)`
:   The StreamRecord class is a case-aware, case-insensitive dictionary implementation.
    
    It has these behaviors:
    - When a key is retrieved, deleted, or checked for existence, it is always checked in a
      case-insensitive manner.
    - The original case is stored in a separate dictionary, so that the original case can be
      retrieved when needed.
    - Because it is subclassed from `dict`, the `StreamRecord` class can be passed as a normal
      Python dictionary.
    - In addition to the properties of the stream's records, the dictionary also stores the Airbyte
      metadata columns: `_airbyte_raw_id`, `_airbyte_extracted_at`, and `_airbyte_meta`.
    
    This behavior mirrors how a case-aware, case-insensitive SQL database would handle column
    references.
    
    There are two ways this class can store keys internally:
    - If normalize_keys is True, the keys are normalized using the given normalizer.
    - If normalize_keys is False, the original case of the keys is stored.
    
    In regards to missing values, the dictionary accepts an 'expected_keys' input. When set, the
    dictionary will be initialized with the given keys. If a key is not found in the input data, it
    will be initialized with a value of None. When provided, the 'expected_keys' input will also
    determine the original case of the keys.
    
    Initialize the dictionary with the given data.
    
    Args:
        from_dict: The dictionary to initialize the StreamRecord with.
        stream_record_handler: The StreamRecordHandler to use for processing the record.
        with_internal_columns: If `True`, the internal columns will be added to the record.
        extracted_at: The time the record was extracted. If not provided, the current time will
            be used.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Static methods

    `from_record_message(record_message: AirbyteRecordMessage, *, stream_record_handler: StreamRecordHandler)`
    :   Return a StreamRecord from a RecordMessage.

`WriteResult(*, destination: AirbyteWriterInterface | Destination, source_data: Source | ReadResult, catalog_provider: CatalogProvider, state_writer: StateWriterBase, progress_tracker: ProgressTracker)`
:   The result of a write operation.
    
    This class is used to return information about the write operation, such as the number of
    records written. It should not be created directly, but instead returned by the write method
    of a destination.
    
    Initialize a write result.
    
    This class should not be created directly. Instead, it should be returned by the `write`
    method of the `Destination` class.

    ### Instance variables

    `processed_records: int`
    :   The total number of records written to the destination.

    ### Methods

    `get_state_provider(self) ‑> StateProviderBase`
    :   Return the state writer as a state provider.
        
        As a public interface, we only expose the state writer as a state provider. This is because
        the state writer itself is only intended for internal use. As a state provider, the state
        writer can be used to read the state artifacts that were written. This can be useful for
        testing or debugging.