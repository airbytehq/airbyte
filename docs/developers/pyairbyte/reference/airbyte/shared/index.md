---
id: airbyte-shared-index
title: airbyte.shared.index
---

Module for future CDK components.

Components here are planned to move to the CDK.

TODO!: Add GitHub link here before merging.

- `airbyte.shared.catalog_providers`
- `airbyte.shared.sql_processor`
- `airbyte.shared.state_providers`
- `airbyte.shared.state_writers`

### `SqlProcessorBase` {#airbyte.shared.SqlProcessorBase}

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

#### Attributes {#airbyte.shared.SqlProcessorBase--attributes}

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

#### `cleanup_all` {#airbyte.shared.SqlProcessorBase.cleanup_all}

<ApiMember kind="method">

<ApiSignature>

```python
def cleanup_all(self) -> None
```

</ApiSignature>

Clean resources.

</ApiMember>

#### `fetch_column_info` {#airbyte.shared.SqlProcessorBase.fetch_column_info}

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

#### `fetch_row_count` {#airbyte.shared.SqlProcessorBase.fetch_row_count}

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

#### `fetch_table_statistics` {#airbyte.shared.SqlProcessorBase.fetch_table_statistics}

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

#### `finalizing_batches` {#airbyte.shared.SqlProcessorBase.finalizing_batches}

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

#### `get_sql_alchemy_url` {#airbyte.shared.SqlProcessorBase.get_sql_alchemy_url}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_alchemy_url(self) -> airbyte.secrets.base.SecretString
```

</ApiSignature>

Return the SQLAlchemy URL to use.

</ApiMember>

#### `get_sql_connection` {#airbyte.shared.SqlProcessorBase.get_sql_connection}

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

#### `get_sql_engine` {#airbyte.shared.SqlProcessorBase.get_sql_engine}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_engine(self) -> Engine
```

</ApiSignature>

Return a new SQL engine to use.

</ApiMember>

#### `get_sql_table` {#airbyte.shared.SqlProcessorBase.get_sql_table}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_table(self, stream_name: str) -> sqlalchemy.sql.schema.Table
```

</ApiSignature>

Return the main table object for the stream.

</ApiMember>

#### `get_sql_table_name` {#airbyte.shared.SqlProcessorBase.get_sql_table_name}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_table_name(self, stream_name: str) -> str
```

</ApiSignature>

Return the name of the SQL table for the given stream.

</ApiMember>

#### `process_airbyte_messages` {#airbyte.shared.SqlProcessorBase.process_airbyte_messages}

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

#### `process_record_message` {#airbyte.shared.SqlProcessorBase.process_record_message}

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

#### `write_stream_data` {#airbyte.shared.SqlProcessorBase.write_stream_data}

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