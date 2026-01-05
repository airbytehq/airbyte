---
sidebar_label: sql_processor
title: airbyte.shared.sql_processor
---

The base SQL Cache implementation.

## annotations

## abc

## contextlib

## enum

## defaultdict

## contextmanager

## cached\_property

## TYPE\_CHECKING

## Any

## cast

## final

## pd

## sqlalchemy

## exc

## ulid

## Index

## BaseModel

## Field

## Column

## Table

## and\_

## create\_engine

## insert

## null

## select

## text

## update

## AirbyteMessage

## AirbyteRecordMessage

## AirbyteStateMessage

## AirbyteStateType

## AirbyteStreamState

## AirbyteTraceMessage

## Type

## exc

## one\_way\_hash

## LowerCaseNormalizer

## AB\_EXTRACTED\_AT\_COLUMN

## AB\_META\_COLUMN

## AB\_RAW\_ID\_COLUMN

## DEBUG\_MODE

## StreamRecordHandler

## SecretString

## StdOutStateWriter

## WriteMethod

## WriteStrategy

## SQLTypeConverter

## RecordDedupeMode Objects

```python
class RecordDedupeMode(enum.Enum)
```

The deduplication mode to use when writing records.

#### APPEND

#### REPLACE

## SQLRuntimeError Objects

```python
class SQLRuntimeError(Exception)
```

Raised when an SQL operation fails.

## SqlConfig Objects

```python
class SqlConfig(BaseModel, abc.ABC)
```

Common configuration for SQL connections.

#### schema\_name

The name of the schema to write to.

#### table\_prefix

A prefix to add to created table names.

#### \_engine

Cached SQL engine instance.

#### get\_sql\_alchemy\_url

```python
@abc.abstractmethod
def get_sql_alchemy_url() -> SecretString
```

Returns a SQL Alchemy URL.

#### get\_database\_name

```python
@abc.abstractmethod
def get_database_name() -> str
```

Return the name of the database.

#### config\_hash

```python
@property
def config_hash() -> str | None
```

Return a unique one-way hash of the configuration.

The generic implementation uses the SQL Alchemy URL, schema name, and table prefix. Some
inputs may be redundant with the SQL Alchemy URL, but this does not hurt the hash
uniqueness.

In most cases, subclasses do not need to override this method.

#### get\_create\_table\_extra\_clauses

```python
def get_create_table_extra_clauses() -> list[str]
```

Return a list of clauses to append on CREATE TABLE statements.

#### get\_sql\_alchemy\_connect\_args

```python
def get_sql_alchemy_connect_args() -> dict[str, Any]
```

Return the SQL Alchemy connect_args.

#### get\_sql\_engine

```python
def get_sql_engine() -> Engine
```

Return a cached SQL engine, creating it if necessary.

#### dispose\_engine

```python
def dispose_engine() -> None
```

Dispose of the cached SQL engine and release all connections.

#### get\_vendor\_client

```python
def get_vendor_client() -> object
```

Return the vendor-specific client object.

This is used for vendor-specific operations.

Raises `NotImplementedError` if a custom vendor client is not defined.

## SqlProcessorBase Objects

```python
class SqlProcessorBase(abc.ABC)
```

A base class to be used for SQL Caches.

#### type\_converter\_class

The type converter class to use for converting JSON schema types to SQL types.

#### normalizer

The name normalizer to user for table and column name normalization.

#### file\_writer\_class

The file writer class to use for writing files to the cache.

#### supports\_merge\_insert

True if the database supports the MERGE INTO syntax.

#### \_\_init\_\_

```python
def __init__(*,
             sql_config: SqlConfig,
             catalog_provider: CatalogProvider,
             state_writer: StateWriterBase | None = None,
             file_writer: FileWriterBase | None = None,
             temp_dir: Path | None = None,
             temp_file_cleanup: bool) -> None
```

Create a new SQL processor.

#### catalog\_provider

```python
@property
def catalog_provider() -> CatalogProvider
```

Return the catalog manager.

Subclasses should set this property to a valid catalog manager instance if one
is not explicitly passed to the constructor.

**Raises**:

- `PyAirbyteInternalError` - If the catalog manager is not set.

#### state\_writer

```python
@property
def state_writer() -> StateWriterBase
```

Return the state writer instance.

Subclasses should set this property to a valid state manager instance if one
is not explicitly passed to the constructor.

**Raises**:

- `PyAirbyteInternalError` - If the state manager is not set.

#### process\_airbyte\_messages

```python
@final
def process_airbyte_messages(
        messages: Iterable[AirbyteMessage],
        *,
        write_strategy: WriteStrategy = WriteStrategy.AUTO,
        progress_tracker: ProgressTracker) -> None
```

Process a stream of Airbyte messages.

This method assumes that the catalog is already registered with the processor.

#### \_write\_all\_stream\_data

```python
def _write_all_stream_data(write_strategy: WriteStrategy,
                           progress_tracker: ProgressTracker) -> None
```

Finalize any pending writes.

#### \_finalize\_state\_messages

```python
def _finalize_state_messages(
        state_messages: list[AirbyteStateMessage]) -> None
```

Handle state messages by passing them to the catalog manager.

#### \_setup

```python
def _setup() -> None
```

Create the database.

By default this is a no-op but subclasses can override this method to prepare
any necessary resources.

#### \_do\_checkpoint

```python
def _do_checkpoint(connection: Connection | None = None) -> None
```

Checkpoint the given connection.

If the WAL log needs to be, it will be flushed.

For most SQL databases, this is a no-op. However, it exists so that
subclasses can override this method to perform a checkpoint operation.

#### sql\_config

```python
@property
def sql_config() -> SqlConfig
```

Return the SQL configuration.

#### get\_sql\_alchemy\_url

```python
def get_sql_alchemy_url() -> SecretString
```

Return the SQLAlchemy URL to use.

#### database\_name

```python
@final
@cached_property
def database_name() -> str
```

Return the name of the database.

#### get\_sql\_engine

```python
@final
def get_sql_engine() -> Engine
```

Return a new SQL engine to use.

#### get\_sql\_connection

```python
@contextmanager
def get_sql_connection(
) -> Generator[sqlalchemy.engine.Connection, None, None]
```

A context manager which returns a new SQL connection for running queries.

If the connection needs to close, it will be closed automatically.

#### get\_sql\_table\_name

```python
def get_sql_table_name(stream_name: str) -> str
```

Return the name of the SQL table for the given stream.

#### get\_sql\_table

```python
@final
def get_sql_table(stream_name: str) -> sqlalchemy.Table
```

Return the main table object for the stream.

#### process\_record\_message

```python
def process_record_message(record_msg: AirbyteRecordMessage,
                           stream_record_handler: StreamRecordHandler,
                           progress_tracker: ProgressTracker) -> None
```

Write a record to the cache.

This method is called for each record message, before the batch is written.

In most cases, the SQL processor will not perform any action, but will pass this along to to
the file processor.

#### \_init\_connection\_settings

```python
def _init_connection_settings(connection: Connection) -> None
```

This is called automatically whenever a new connection is created.

By default this is a no-op. Subclasses can use this to set connection settings, such as
timezone, case-sensitivity settings, and other session-level variables.

#### \_invalidate\_table\_cache

```python
def _invalidate_table_cache(table_name: str) -> None
```

Invalidate the the named table cache.

This should be called whenever the table schema is known to have changed.

#### \_get\_table\_by\_name

```python
def _get_table_by_name(table_name: str,
                       *,
                       force_refresh: bool = False,
                       shallow_okay: bool = False) -> sqlalchemy.Table
```

Return a table object from a table name.

If &#x27;shallow_okay&#x27; is True, the table will be returned without requiring properties to
be read from the database.

To prevent unnecessary round-trips to the database, the table is cached after the first
query. To ignore the cache and force a refresh, set &#x27;force_refresh&#x27; to True.

#### \_ensure\_schema\_exists

```python
def _ensure_schema_exists() -> None
```

#### \_quote\_identifier

```python
def _quote_identifier(identifier: str) -> str
```

Return the given identifier, quoted.

#### \_get\_temp\_table\_name

```python
@final
def _get_temp_table_name(stream_name: str, batch_id: str | None = None) -> str
```

Return a new (unique) temporary table name.

#### \_fully\_qualified

```python
def _fully_qualified(table_name: str) -> str
```

Return the fully qualified name of the given table.

#### \_create\_table\_for\_loading

```python
@final
def _create_table_for_loading(stream_name: str, batch_id: str) -> str
```

Create a new table for loading data.

#### \_get\_tables\_list

```python
def _get_tables_list() -> list[str]
```

Return a list of all tables in the database.

#### \_get\_schemas\_list

```python
def _get_schemas_list(database_name: str | None = None,
                      *,
                      force_refresh: bool = False) -> list[str]
```

Return a list of all tables in the database.

#### \_ensure\_final\_table\_exists

```python
def _ensure_final_table_exists(stream_name: str,
                               *,
                               create_if_missing: bool = True) -> str
```

Create the final table if it doesn&#x27;t already exist.

Return the table name.

#### \_ensure\_compatible\_table\_schema

```python
def _ensure_compatible_table_schema(stream_name: str, table_name: str) -> None
```

Return true if the given table is compatible with the stream&#x27;s schema.

Raises an exception if the table schema is not compatible with the schema of the
input stream.

#### \_create\_table

```python
@final
def _create_table(table_name: str,
                  column_definition_str: str,
                  primary_keys: list[str] | None = None) -> None
```

#### \_get\_sql\_column\_definitions

```python
@final
def _get_sql_column_definitions(
        stream_name: str) -> dict[str, sqlalchemy.types.TypeEngine]
```

Return the column definitions for the given stream.

#### write\_stream\_data

```python
@final
def write_stream_data(stream_name: str,
                      *,
                      write_method: WriteMethod | None = None,
                      write_strategy: WriteStrategy | None = None,
                      progress_tracker: ProgressTracker) -> list[BatchHandle]
```

Finalize all uncommitted batches.

This is a generic &#x27;final&#x27; SQL implementation, which should not be overridden.

Returns a mapping of batch IDs to batch handles, for those processed batches.

TODO: Add a dedupe step here to remove duplicates from the temp table.
      Some sources will send us duplicate records within the same stream,
      although this is a fairly rare edge case we can ignore in V1.

#### cleanup\_all

```python
@final
def cleanup_all() -> None
```

Clean resources.

#### finalizing\_batches

```python
@final
@contextlib.contextmanager
def finalizing_batches(
    stream_name: str, progress_tracker: ProgressTracker
) -> Generator[list[BatchHandle], str, None]
```

Context manager to use for finalizing batches, if applicable.

Returns a mapping of batch IDs to batch handles, for those processed batches.

#### \_execute\_sql

```python
def _execute_sql(sql: str | TextClause | Executable) -> CursorResult
```

Execute the given SQL statement.

#### \_drop\_temp\_table

```python
def _drop_temp_table(table_name: str, *, if_exists: bool = True) -> None
```

Drop the given table.

#### \_write\_files\_to\_new\_table

```python
def _write_files_to_new_table(files: list[Path], stream_name: str,
                              batch_id: str) -> str
```

Write a file(s) to a new table.

This is a generic implementation, which can be overridden by subclasses
to improve performance.

#### \_add\_column\_to\_table

```python
def _add_column_to_table(table: Table, column_name: str,
                         column_type: sqlalchemy.types.TypeEngine) -> None
```

Add a column to the given table.

#### \_add\_missing\_columns\_to\_table

```python
def _add_missing_columns_to_table(stream_name: str, table_name: str) -> None
```

Add missing columns to the table.

This is a no-op if all columns are already present.

#### \_write\_temp\_table\_to\_final\_table

```python
@final
def _write_temp_table_to_final_table(stream_name: str, temp_table_name: str,
                                     final_table_name: str,
                                     write_method: WriteMethod) -> None
```

Write the temp table into the final table using the provided write strategy.

#### \_append\_temp\_table\_to\_final\_table

```python
def _append_temp_table_to_final_table(temp_table_name: str,
                                      final_table_name: str,
                                      stream_name: str) -> None
```

#### \_swap\_temp\_table\_with\_final\_table

```python
def _swap_temp_table_with_final_table(stream_name: str, temp_table_name: str,
                                      final_table_name: str) -> None
```

Merge the temp table into the main one.

This implementation requires MERGE support in the SQL DB.
Databases that do not support this syntax can override this method.

#### \_merge\_temp\_table\_to\_final\_table

```python
def _merge_temp_table_to_final_table(stream_name: str, temp_table_name: str,
                                     final_table_name: str) -> None
```

Merge the temp table into the main one.

This implementation requires MERGE support in the SQL DB.
Databases that do not support this syntax can override this method.

#### \_get\_column\_by\_name

```python
def _get_column_by_name(table: str | Table, column_name: str) -> Column
```

Return the column object for the given column name.

This method is case-insensitive.

#### \_emulated\_merge\_temp\_table\_to\_final\_table

```python
def _emulated_merge_temp_table_to_final_table(stream_name: str,
                                              temp_table_name: str,
                                              final_table_name: str) -> None
```

Emulate the merge operation using a series of SQL commands.

This is a fallback implementation for databases that do not support MERGE.

#### \_table\_exists

```python
def _table_exists(table_name: str) -> bool
```

Return true if the given table exists.

Subclasses may override this method to provide a more efficient implementation.

