---
id: airbyte-shared-sql_processor
title: airbyte.shared.sql_processor
---

The base SQL Cache implementation.

### `ColumnStatistics` {#airbyte.shared.sql_processor.ColumnStatistics}

<ApiMember kind="class">

<ApiSignature>

```python
class ColumnStatistics(**data: Any)
```

</ApiSignature>

Null/non-null statistics for a single column.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.shared.sql_processor.ColumnStatistics--attributes}

- **`column_name`**&nbsp;(`str`)

  The column name as found in the destination.

- **`column_type`**&nbsp;(`str`)

  The SQL data type name as reported by the database.

- **`non_null_count`**&nbsp;(`int | None`)

  Number of non-NULL values in this column.

- **`null_count`**&nbsp;(`int | None`)

  Number of NULL values in this column.

- **`total_count`**&nbsp;(`int | None`)

  Total row count (null_count + non_null_count).

</ApiMember>

### `RecordDedupeMode` {#airbyte.shared.sql_processor.RecordDedupeMode}

<ApiMember kind="class">

<ApiSignature>

```python
class RecordDedupeMode(
    value,
    names=None,
    *,
    module=None,
    qualname=None,
    type=None,
    start=1,
)
```

</ApiSignature>

The deduplication mode to use when writing records.

**Bases:** `enum.Enum`

#### Attributes {#airbyte.shared.sql_processor.RecordDedupeMode--attributes}

- **`APPEND`**

- **`REPLACE`**

</ApiMember>

### `SQLRuntimeError` {#airbyte.shared.sql_processor.SQLRuntimeError}

<ApiMember kind="class">

<ApiSignature>

```python
class SQLRuntimeError(*args, **kwargs)
```

</ApiSignature>

Raised when an SQL operation fails.

**Bases:** `builtins.Exception`, `builtins.BaseException`

</ApiMember>

### `SqlConfig` {#airbyte.shared.sql_processor.SqlConfig}

<ApiMember kind="class">

<ApiSignature>

```python
class SqlConfig(**data: Any)
```

</ApiSignature>

Common configuration for SQL connections.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

**Bases:** `abc.ABC`

**Subclasses:** `airbyte._processors.sql.bigquery.BigQueryConfig`, `airbyte._processors.sql.duckdb.DuckDBConfig`, `airbyte._processors.sql.postgres.PostgresConfig`, `airbyte._processors.sql.snowflake.SnowflakeConfig`, `airbyte.caches.base.CacheBase`

#### Attributes {#airbyte.shared.sql_processor.SqlConfig--attributes}

- **`schema_name`**&nbsp;(`str`)

  The name of the schema to write to.

- **`table_prefix`**&nbsp;(`str | None`)

  A prefix to add to created table names.

- **`config_hash`**&nbsp;(`str | None`)

  Return a unique one-way hash of the configuration.

  The generic implementation uses the SQL Alchemy URL, schema name, and table prefix. Some
  inputs may be redundant with the SQL Alchemy URL, but this does not hurt the hash
  uniqueness.

  In most cases, subclasses do not need to override this method.

#### `dispose_engine` {#airbyte.shared.sql_processor.SqlConfig.dispose_engine}

<ApiMember kind="method">

<ApiSignature>

```python
def dispose_engine(self) -> None
```

</ApiSignature>

Dispose of the cached SQL engine and release all connections.

</ApiMember>

#### `get_create_table_extra_clauses` {#airbyte.shared.sql_processor.SqlConfig.get_create_table_extra_clauses}

<ApiMember kind="method">

<ApiSignature>

```python
def get_create_table_extra_clauses(self) -> list[str]
```

</ApiSignature>

Return a list of clauses to append on CREATE TABLE statements.

</ApiMember>

#### `get_database_name` {#airbyte.shared.sql_processor.SqlConfig.get_database_name}

<ApiMember kind="method">

<ApiSignature>

```python
def get_database_name(self) -> str
```

</ApiSignature>

Return the name of the database.

</ApiMember>

#### `get_sql_alchemy_connect_args` {#airbyte.shared.sql_processor.SqlConfig.get_sql_alchemy_connect_args}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_alchemy_connect_args(self) -> dict[str, typing.Any]
```

</ApiSignature>

Return the SQL Alchemy connect_args.

</ApiMember>

#### `get_sql_alchemy_url` {#airbyte.shared.sql_processor.SqlConfig.get_sql_alchemy_url}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_alchemy_url(self) -> airbyte.secrets.base.SecretString
```

</ApiSignature>

Returns a SQL Alchemy URL.

</ApiMember>

#### `get_sql_engine` {#airbyte.shared.sql_processor.SqlConfig.get_sql_engine}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_engine(self) -> Engine
```

</ApiSignature>

Return a cached SQL engine, creating it if necessary.

</ApiMember>

#### `get_vendor_client` {#airbyte.shared.sql_processor.SqlConfig.get_vendor_client}

<ApiMember kind="method">

<ApiSignature>

```python
def get_vendor_client(self) -> object
```

</ApiSignature>

Return the vendor-specific client object.

This is used for vendor-specific operations.

Raises `NotImplementedError` if a custom vendor client is not defined.

</ApiMember>

</ApiMember>

### `SqlProcessorBase` {#airbyte.shared.sql_processor.SqlProcessorBase}

<ApiMember kind="class">

<ApiSignature>

```python
class SqlProcessorBase(
    *,
    sql_config: SqlConfig,
    catalog_provider: CatalogProvider,
    state_writer: StateWriterBase | None = None,
    file_writer: FileWriterBase | None = None,
    temp_dir: Path | None = None,
    temp_file_cleanup: bool,
)
```

</ApiSignature>

A base class to be used for SQL Caches.

Create a new SQL processor.

**Bases:** `abc.ABC`

**Subclasses:** `airbyte._processors.sql.bigquery.BigQuerySqlProcessor`, `airbyte._processors.sql.duckdb.DuckDBSqlProcessor`, `airbyte._processors.sql.postgres.PostgresSqlProcessor`, `airbyte._processors.sql.snowflake.SnowflakeSqlProcessor`

#### Attributes {#airbyte.shared.sql_processor.SqlProcessorBase--attributes}

- **`file_writer_class`**&nbsp;(`type[FileWriterBase]`)

  The file writer class to use for writing files to the cache.

- **`normalizer`**

  The name normalizer to user for table and column name normalization.

- **`supports_merge_insert`**

  True if the database supports the MERGE INTO syntax.

- **`type_converter_class`**&nbsp;(`type[SQLTypeConverter]`)

  The type converter class to use for converting JSON schema types to SQL types.

- **`catalog_provider`**&nbsp;(`CatalogProvider`)

  Return the catalog manager.

  Subclasses should set this property to a valid catalog manager instance if one
  is not explicitly passed to the constructor.

  **Raises:**

  - **`PyAirbyteInternalError`**: If the catalog manager is not set.

- **`database_name`**&nbsp;(`str`)

  Return the name of the database.

- **`sql_config`**&nbsp;(`SqlConfig`)

  Return the SQL configuration.

- **`state_writer`**&nbsp;(`StateWriterBase`)

  Return the state writer instance.

  Subclasses should set this property to a valid state manager instance if one
  is not explicitly passed to the constructor.

  **Raises:**

  - **`PyAirbyteInternalError`**: If the state manager is not set.

#### `cleanup_all` {#airbyte.shared.sql_processor.SqlProcessorBase.cleanup_all}

<ApiMember kind="method">

<ApiSignature>

```python
def cleanup_all(self) -> None
```

</ApiSignature>

Clean resources.

</ApiMember>

#### `fetch_column_info` {#airbyte.shared.sql_processor.SqlProcessorBase.fetch_column_info}

<ApiMember kind="method">

<ApiSignature>

```python
def fetch_column_info(
    self,
    table_name: str,
    *,
    inspector: Inspector | None = None,
) -> list[dict[str, str]]
```

</ApiSignature>

Return actual column names and types for the given table.

This method differs from `_get_sql_column_definitions` in that it always
returns actual detected column types from the database. It will never
return previously-cached types or 'expected' types based on the stream
JSON schema.

Each entry is a dict with `column_name` and `column_type` keys.

**Args:**

- **`table_name`**: The table to inspect.
- **`inspector`**: An optional pre-created SQLAlchemy `Inspector` to reuse. When inspecting many tables, passing a shared inspector avoids creating a new one per call.

Raises if the table does not exist or is not accessible.

</ApiMember>

#### `fetch_row_count` {#airbyte.shared.sql_processor.SqlProcessorBase.fetch_row_count}

<ApiMember kind="method">

<ApiSignature>

```python
def fetch_row_count(self, table_name: str) -> int
```

</ApiSignature>

Return the number of rows in the given table.

Raises `SQLRuntimeError` if the table does not exist or the query
fails for any other reason.

</ApiMember>

#### `fetch_table_statistics` {#airbyte.shared.sql_processor.SqlProcessorBase.fetch_table_statistics}

<ApiMember kind="method">

<ApiSignature>

```python
def fetch_table_statistics(
    self,
    stream_names: list[str],
) -> dict[str, airbyte.shared.sql_processor.TableStatistics]
```

</ApiSignature>

Return table statistics for the given stream names.

For each stream, resolves the expected table name via the processor's
normalizer, queries row counts, column info, and per-column null/non-null
stats.

If the normalized table name is not found, falls back to the original
stream name (some destinations preserve original casing).

Returns a dict mapping stream name to a `TableStatistics` instance.
Streams whose tables are not found are omitted from the result.

</ApiMember>

#### `finalizing_batches` {#airbyte.shared.sql_processor.SqlProcessorBase.finalizing_batches}

<ApiMember kind="method">

<ApiSignature>

```python
def finalizing_batches(
    self,
    stream_name: str,
    progress_tracker: ProgressTracker,
) -> Generator[list[BatchHandle], str, None]
```

</ApiSignature>

Context manager to use for finalizing batches, if applicable.

Returns a mapping of batch IDs to batch handles, for those processed batches.

</ApiMember>

#### `get_sql_alchemy_url` {#airbyte.shared.sql_processor.SqlProcessorBase.get_sql_alchemy_url}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_alchemy_url(self) -> airbyte.secrets.base.SecretString
```

</ApiSignature>

Return the SQLAlchemy URL to use.

</ApiMember>

#### `get_sql_connection` {#airbyte.shared.sql_processor.SqlProcessorBase.get_sql_connection}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_connection(
    self,
) -> Generator[sqlalchemy.engine.Connection, None, None]
```

</ApiSignature>

A context manager which returns a new SQL connection for running queries.

If the connection needs to close, it will be closed automatically.

</ApiMember>

#### `get_sql_engine` {#airbyte.shared.sql_processor.SqlProcessorBase.get_sql_engine}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_engine(self) -> Engine
```

</ApiSignature>

Return a new SQL engine to use.

</ApiMember>

#### `get_sql_table` {#airbyte.shared.sql_processor.SqlProcessorBase.get_sql_table}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_table(self, stream_name: str) -> sqlalchemy.sql.schema.Table
```

</ApiSignature>

Return the main table object for the stream.

</ApiMember>

#### `get_sql_table_name` {#airbyte.shared.sql_processor.SqlProcessorBase.get_sql_table_name}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_table_name(self, stream_name: str) -> str
```

</ApiSignature>

Return the name of the SQL table for the given stream.

</ApiMember>

#### `process_airbyte_messages` {#airbyte.shared.sql_processor.SqlProcessorBase.process_airbyte_messages}

<ApiMember kind="method">

<ApiSignature>

```python
def process_airbyte_messages(
    self,
    messages: Iterable[AirbyteMessage],
    *,
    write_strategy: WriteStrategy = WriteStrategy.AUTO,
    progress_tracker: ProgressTracker,
) -> None
```

</ApiSignature>

Process a stream of Airbyte messages.

This method assumes that the catalog is already registered with the processor.

</ApiMember>

#### `process_record_message` {#airbyte.shared.sql_processor.SqlProcessorBase.process_record_message}

<ApiMember kind="method">

<ApiSignature>

```python
def process_record_message(
    self,
    record_msg: AirbyteRecordMessage,
    stream_record_handler: StreamRecordHandler,
    progress_tracker: ProgressTracker,
) -> None
```

</ApiSignature>

Write a record to the cache.

This method is called for each record message, before the batch is written.

In most cases, the SQL processor will not perform any action, but will pass this along to to
the file processor.

</ApiMember>

#### `write_stream_data` {#airbyte.shared.sql_processor.SqlProcessorBase.write_stream_data}

<ApiMember kind="method">

<ApiSignature>

```python
def write_stream_data(
    self,
    stream_name: str,
    *,
    write_method: WriteMethod | None = None,
    write_strategy: WriteStrategy | None = None,
    progress_tracker: ProgressTracker,
) -> list[BatchHandle]
```

</ApiSignature>

Finalize all uncommitted batches.

This is a generic 'final' SQL implementation, which should not be overridden.

Returns a mapping of batch IDs to batch handles, for those processed batches.

TODO: Add a dedupe step here to remove duplicates from the temp table.
      Some sources will send us duplicate records within the same stream,
      although this is a fairly rare edge case we can ignore in V1.

</ApiMember>

</ApiMember>

### `TableStatistics` {#airbyte.shared.sql_processor.TableStatistics}

<ApiMember kind="class">

<ApiSignature>

```python
class TableStatistics(**data: Any)
```

</ApiSignature>

Statistics for a single table: row count, column info, and per-column stats.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.shared.sql_processor.TableStatistics--attributes}

- **`column_statistics`**&nbsp;(`list[airbyte.shared.sql_processor.ColumnStatistics]`)

  Per-column names, types, and null/non-null statistics.

- **`database_name`**&nbsp;(`str | None`)

  The database name where this table resides.

- **`row_count`**&nbsp;(`int | None`)

  Number of rows found.

- **`schema_name`**&nbsp;(`str | None`)

  The schema name where this table resides.

- **`table_name`**&nbsp;(`str`)

  The table name as found in the destination.

</ApiMember>