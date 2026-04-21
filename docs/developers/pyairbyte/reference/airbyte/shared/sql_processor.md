---
id: airbyte-shared-sql_processor
title: airbyte.shared.sql_processor
---

Module airbyte.shared.sql_processor
===================================
The base SQL Cache implementation.

Classes
-------

`RecordDedupeMode(*args, **kwds)`
:   The deduplication mode to use when writing records.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `APPEND`
    :

    `REPLACE`
    :

`SQLRuntimeError(*args, **kwargs)`
:   Raised when an SQL operation fails.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`SqlConfig(**data: Any)`
:   Common configuration for SQL connections.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * abc.ABC

    ### Descendants

    * airbyte._processors.sql.bigquery.BigQueryConfig
    * airbyte._processors.sql.duckdb.DuckDBConfig
    * airbyte._processors.sql.postgres.PostgresConfig
    * airbyte._processors.sql.snowflake.SnowflakeConfig
    * airbyte.caches.base.CacheBase

    ### Class variables

    `model_config`
    :

    `schema_name: str`
    :   The name of the schema to write to.

    `table_prefix: str | None`
    :   A prefix to add to created table names.

    ### Instance variables

    `config_hash: str | None`
    :   Return a unique one-way hash of the configuration.
        
        The generic implementation uses the SQL Alchemy URL, schema name, and table prefix. Some
        inputs may be redundant with the SQL Alchemy URL, but this does not hurt the hash
        uniqueness.
        
        In most cases, subclasses do not need to override this method.

    ### Methods

    `dispose_engine(self) ‑> None`
    :   Dispose of the cached SQL engine and release all connections.

    `get_create_table_extra_clauses(self) ‑> list[str]`
    :   Return a list of clauses to append on CREATE TABLE statements.

    `get_database_name(self) ‑> str`
    :   Return the name of the database.

    `get_sql_alchemy_connect_args(self) ‑> dict[str, typing.Any]`
    :   Return the SQL Alchemy connect_args.

    `get_sql_alchemy_url(self) ‑> airbyte.secrets.base.SecretString`
    :   Returns a SQL Alchemy URL.

    `get_sql_engine(self) ‑> Engine`
    :   Return a cached SQL engine, creating it if necessary.

    `get_vendor_client(self) ‑> object`
    :   Return the vendor-specific client object.
        
        This is used for vendor-specific operations.
        
        Raises `NotImplementedError` if a custom vendor client is not defined.

    `model_post_init(self: BaseModel, context: Any, /) ‑> None`
    :   This function is meant to behave like a BaseModel method to initialise private attributes.
        
        It takes context as an argument since that's what pydantic-core passes when calling it.
        
        Args:
            self: The BaseModel instance.
            context: The context.

`SqlProcessorBase(*, sql_config: SqlConfig, catalog_provider: CatalogProvider, state_writer: StateWriterBase | None = None, file_writer: FileWriterBase | None = None, temp_dir: Path | None = None, temp_file_cleanup: bool)`
:   A base class to be used for SQL Caches.
    
    Create a new SQL processor.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte._processors.sql.bigquery.BigQuerySqlProcessor
    * airbyte._processors.sql.duckdb.DuckDBSqlProcessor
    * airbyte._processors.sql.postgres.PostgresSqlProcessor
    * airbyte._processors.sql.snowflake.SnowflakeSqlProcessor

    ### Class variables

    `file_writer_class: type[FileWriterBase]`
    :   The file writer class to use for writing files to the cache.

    `normalizer`
    :   The name normalizer to user for table and column name normalization.

    `supports_merge_insert`
    :   True if the database supports the MERGE INTO syntax.

    `type_converter_class: type[SQLTypeConverter]`
    :   The type converter class to use for converting JSON schema types to SQL types.

    ### Instance variables

    `catalog_provider: CatalogProvider`
    :   Return the catalog manager.
        
        Subclasses should set this property to a valid catalog manager instance if one
        is not explicitly passed to the constructor.
        
        Raises:
            PyAirbyteInternalError: If the catalog manager is not set.

    `database_name: str`
    :   Return the name of the database.

    `sql_config: SqlConfig`
    :   Return the SQL configuration.

    `state_writer: StateWriterBase`
    :   Return the state writer instance.
        
        Subclasses should set this property to a valid state manager instance if one
        is not explicitly passed to the constructor.
        
        Raises:
            PyAirbyteInternalError: If the state manager is not set.

    ### Methods

    `cleanup_all(self) ‑> None`
    :   Clean resources.

    `finalizing_batches(self, stream_name: str, progress_tracker: ProgressTracker) ‑> Generator[list[BatchHandle], str, None]`
    :   Context manager to use for finalizing batches, if applicable.
        
        Returns a mapping of batch IDs to batch handles, for those processed batches.

    `get_sql_alchemy_url(self) ‑> airbyte.secrets.base.SecretString`
    :   Return the SQLAlchemy URL to use.

    `get_sql_connection(self) ‑> Generator[sqlalchemy.engine.Connection, None, None]`
    :   A context manager which returns a new SQL connection for running queries.
        
        If the connection needs to close, it will be closed automatically.

    `get_sql_engine(self) ‑> Engine`
    :   Return a new SQL engine to use.

    `get_sql_table(self, stream_name: str) ‑> sqlalchemy.sql.schema.Table`
    :   Return the main table object for the stream.

    `get_sql_table_name(self, stream_name: str) ‑> str`
    :   Return the name of the SQL table for the given stream.

    `process_airbyte_messages(self, messages: Iterable[AirbyteMessage], *, write_strategy: WriteStrategy = WriteStrategy.AUTO, progress_tracker: ProgressTracker) ‑> None`
    :   Process a stream of Airbyte messages.
        
        This method assumes that the catalog is already registered with the processor.

    `process_record_message(self, record_msg: AirbyteRecordMessage, stream_record_handler: StreamRecordHandler, progress_tracker: ProgressTracker) ‑> None`
    :   Write a record to the cache.
        
        This method is called for each record message, before the batch is written.
        
        In most cases, the SQL processor will not perform any action, but will pass this along to to
        the file processor.

    `write_stream_data(self, stream_name: str, *, write_method: WriteMethod | None = None, write_strategy: WriteStrategy | None = None, progress_tracker: ProgressTracker) ‑> list[BatchHandle]`
    :   Finalize all uncommitted batches.
        
        This is a generic 'final' SQL implementation, which should not be overridden.
        
        Returns a mapping of batch IDs to batch handles, for those processed batches.
        
        TODO: Add a dedupe step here to remove duplicates from the temp table.
              Some sources will send us duplicate records within the same stream,
              although this is a fairly rare edge case we can ignore in V1.