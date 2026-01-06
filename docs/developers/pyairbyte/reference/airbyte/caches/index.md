---
id: airbyte-caches-index
title: airbyte.caches.index
---

Module airbyte.caches
=====================
Base module for all caches.

Sub-modules
-----------
* airbyte.caches.base
* airbyte.caches.bigquery
* airbyte.caches.duckdb
* airbyte.caches.generic
* airbyte.caches.motherduck
* airbyte.caches.postgres
* airbyte.caches.snowflake
* airbyte.caches.util

Functions
---------

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

`CacheBase(**data: Any)`
:   Base configuration for a cache.
    
    Caches inherit from the matching `SqlConfig` class, which provides the SQL config settings
    and basic connectivity to the SQL database.
    
    The cache is responsible for managing the state of the data synced to the cache, including the
    stream catalog and stream state. The cache also provides the mechanism to read and write data
    to the SQL backend specified in the `SqlConfig` class.
    
    Initialize the cache and backends.

    ### Ancestors (in MRO)

    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Descendants

    * airbyte.caches.bigquery.BigQueryCache
    * airbyte.caches.duckdb.DuckDBCache
    * airbyte.caches.generic.GenericSQLCacheConfig
    * airbyte.caches.postgres.PostgresCache
    * airbyte.caches.snowflake.SnowflakeCache

    ### Class variables

    `cache_dir: Path`
    :   The directory to store the cache in.

    `cleanup: bool`
    :   Whether to clean up the cache after use.

    `model_config`
    :

    `paired_destination_config_class: ClassVar[type | None]`
    :

    `paired_destination_name: ClassVar[str | None]`
    :

    ### Instance variables

    `config_hash: str | None`
    :   Return a hash of the cache configuration.
        
        This is the same as the SQLConfig hash from the superclass.

    `paired_destination_config: Any | dict[str, Any]`
    :   Return a dictionary of destination configuration values.

    `processor: SqlProcessorBase`
    :   Return the SQL processor instance.

    `streams: dict[str, CachedDataset]`
    :   Return a temporary table name.

    ### Methods

    `close(self) ‑> None`
    :   Close all database connections and dispose of connection pools.
        
        This method ensures that all SQLAlchemy engines created by this cache
        and its processors are properly disposed, releasing all database connections.
        This is especially important for file-based databases like DuckDB, which
        lock the database file until all connections are closed.
        
        This method is idempotent and can be called multiple times safely.
        
        Raises:
            Exception: If any engine disposal fails, the exception will propagate
                to the caller. This ensures callers are aware of cleanup failures.

    `create_source_tables(self, source: Source, streams: "Literal['*'] | list[str] | None" = None) ‑> None`
    :   Create tables in the cache for the provided source if they do not exist already.
        
        Tables are created based upon the Source's catalog.
        
        Args:
            source: The source to create tables for.
            streams: Stream names to create tables for. If None, use the Source's selected_streams
                or "*" if neither is set. If "*", all available streams will be used.

    `execute_sql(self, sql: str | list[str]) ‑> None`
    :   Execute one or more SQL statements against the cache's SQL backend.
        
        If multiple SQL statements are given, they are executed in order,
        within the same transaction.
        
        This method is useful for creating tables, indexes, and other
        schema objects in the cache. It does not return any results and it
        automatically closes the connection after executing all statements.
        
        This method is not intended for querying data. For that, use the `get_records`
        method - or for a low-level interface, use the `get_sql_engine` method.
        
        If any of the statements fail, the transaction is canceled and an exception
        is raised. Most databases will rollback the transaction in this case.

    `get_arrow_dataset(self, stream_name: str, *, max_chunk_size: int = 100000) ‑> pyarrow._dataset.Dataset`
    :   Return an Arrow Dataset with the stream's data.

    `get_pandas_dataframe(self, stream_name: str) ‑> pandas.core.frame.DataFrame`
    :   Return a Pandas data frame with the stream's data.

    `get_record_processor(self, source_name: str, catalog_provider: CatalogProvider, state_writer: StateWriterBase | None = None) ‑> SqlProcessorBase`
    :   Return a record processor for the specified source name and catalog.
        
        We first register the source and its catalog with the catalog manager. Then we create a new
        SQL processor instance with (only) the given input catalog.
        
        For the state writer, we use a state writer which stores state in an internal SQL table.

    `get_records(self, stream_name: str) ‑> airbyte.datasets._sql.CachedDataset`
    :   Uses SQLAlchemy to select all rows from the table.

    `get_state_provider(self, source_name: str, *, refresh: bool = True, destination_name: str | None = None) ‑> StateProviderBase`
    :   Return a state provider for the specified source name.

    `get_state_writer(self, source_name: str, destination_name: str | None = None) ‑> StateWriterBase`
    :   Return a state writer for the specified source name.
        
        If syncing to the cache, `destination_name` should be `None`.
        If syncing to a destination, `destination_name` should be the destination name.

    `register_source(self, source_name: str, incoming_source_catalog: ConfiguredAirbyteCatalog, stream_names: set[str]) ‑> None`
    :   Register the source name and catalog.

    `run_sql_query(self, sql_query: str, *, max_records: int | None = None) ‑> list[dict[str, typing.Any]]`
    :   Run a SQL query against the cache and return results as a list of dictionaries.
        
        This method is designed for single DML statements like SELECT, SHOW, or DESCRIBE.
        For DDL statements or multiple statements, use the processor directly.
        
        Args:
            sql_query: The SQL query to execute
            max_records: Maximum number of records to return. If None, returns all records.
        
        Returns:
            List of dictionaries representing the query results

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

`MotherDuckCache(**data: Any)`
:   Cache that uses MotherDuck for external persistent storage.
    
    Initialize the cache and backends.

    ### Ancestors (in MRO)

    * airbyte.caches.motherduck.MotherDuckConfig
    * airbyte.caches.duckdb.DuckDBCache
    * airbyte._processors.sql.duckdb.DuckDBConfig
    * airbyte.caches.base.CacheBase
    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Class variables

    `model_config`
    :

    `paired_destination_name: ClassVar[str | None]`
    :

`PostgresCache(**data: Any)`
:   Configuration for the Postgres cache.
    
    Also inherits config from the JsonlWriter, which is responsible for writing files to disk.
    
    Initialize the cache and backends.

    ### Ancestors (in MRO)

    * airbyte._processors.sql.postgres.PostgresConfig
    * airbyte.caches.base.CacheBase
    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Class variables

    `model_config`
    :

    `paired_destination_config_class: ClassVar[type | None]`
    :   DestinationPostgres(database: 'str', host: 'str', username: 'str', DESTINATION_TYPE: 'Final[Postgres]' = &lt;Postgres.POSTGRES: 'postgres'&gt;, disable_type_dedupe: 'Optional[bool]' = False, drop_cascade: 'Optional[bool]' = False, jdbc_url_params: 'Optional[str]' = None, password: 'Optional[str]' = None, port: 'Optional[int]' = 5432, raw_data_schema: 'Optional[str]' = None, schema: 'Optional[str]' = 'public', ssl: 'Optional[bool]' = False, ssl_mode: 'Optional[SSLModes]' = None, tunnel_method: 'Optional[DestinationPostgresSSHTunnelMethod]' = None, unconstrained_number: 'Optional[bool]' = False)

    `paired_destination_name: ClassVar[str | None]`
    :

    ### Methods

    `clone_as_cloud_destination_config(self) ‑> airbyte_api.models.destination_postgres.DestinationPostgres`
    :   Return a DestinationPostgres instance with the same configuration.

`SnowflakeCache(**data: Any)`
:   Configuration for the Snowflake cache.
    
    Initialize the cache and backends.

    ### Ancestors (in MRO)

    * airbyte._processors.sql.snowflake.SnowflakeConfig
    * airbyte.caches.base.CacheBase
    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Class variables

    `dedupe_mode: RecordDedupeMode`
    :

    `model_config`
    :

    `paired_destination_config_class: ClassVar[type | None]`
    :   DestinationSnowflake(database: 'str', host: 'str', role: 'str', schema: 'str', username: 'str', warehouse: 'str', credentials: 'Optional[AuthorizationMethod]' = None, DESTINATION_TYPE: 'Final[Snowflake]' = &lt;Snowflake.SNOWFLAKE: 'snowflake'&gt;, disable_type_dedupe: 'Optional[bool]' = False, jdbc_url_params: 'Optional[str]' = None, raw_data_schema: 'Optional[str]' = None, retention_period_days: 'Optional[int]' = 1, use_merge_for_upsert: 'Optional[bool]' = False)

    `paired_destination_name: ClassVar[str | None]`
    :