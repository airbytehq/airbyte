---
id: airbyte-caches-base
title: airbyte.caches.base
---

SQL Cache implementation.

### `CacheBase` {#airbyte.caches.base.CacheBase}

<ApiMember kind="class">

<ApiSignature>

```python
class CacheBase(**data: Any)
```

</ApiSignature>

Base configuration for a cache.

Caches inherit from the matching `SqlConfig` class, which provides the SQL config settings
and basic connectivity to the SQL database.

The cache is responsible for managing the state of the data synced to the cache, including the
stream catalog and stream state. The cache also provides the mechanism to read and write data
to the SQL backend specified in the `SqlConfig` class.

Initialize the cache and backends.

**Bases:** `airbyte.shared.sql_processor.SqlConfig`, `airbyte._writers.base.AirbyteWriterInterface`, `abc.ABC`

**Subclasses:** `airbyte.caches.bigquery.BigQueryCache`, `airbyte.caches.duckdb.DuckDBCache`, `airbyte.caches.generic.GenericSQLCacheConfig`, `airbyte.caches.postgres.PostgresCache`, `airbyte.caches.snowflake.SnowflakeCache`

#### Attributes {#airbyte.caches.base.CacheBase--attributes}

- **`cache_dir`**&nbsp;(`Path`) — The directory to store the cache in.

- **`cleanup`**&nbsp;(`bool`) — Whether to clean up the cache after use.

- **`paired_destination_config_class`**&nbsp;(`ClassVar[type | None]`)

- **`paired_destination_name`**&nbsp;(`ClassVar[str | None]`)

- **`config_hash`**&nbsp;(`str | None`) — Return a hash of the cache configuration.  This is the same as the SQLConfig hash from the superclass.

- **`paired_destination_config`**&nbsp;(`Any | dict[str, Any]`) — Return a dictionary of destination configuration values.

- **`processor`**&nbsp;(`SqlProcessorBase`) — Return the SQL processor instance.

- **`streams`**&nbsp;(`dict[str, CachedDataset]`) — Return a temporary table name.

#### `close` {#airbyte.caches.base.CacheBase.close}

<ApiMember kind="method">

<ApiSignature>

```python
def close(self) -> None
```

</ApiSignature>

Close all database connections and dispose of connection pools.

This method ensures that all SQLAlchemy engines created by this cache
and its processors are properly disposed, releasing all database connections.
This is especially important for file-based databases like DuckDB, which
lock the database file until all connections are closed.

This method is idempotent and can be called multiple times safely.

**Raises:**

- **`Exception`**: If any engine disposal fails, the exception will propagate to the caller. This ensures callers are aware of cleanup failures.

</ApiMember>

#### `create_source_tables` {#airbyte.caches.base.CacheBase.create_source_tables}

<ApiMember kind="method">

<ApiSignature>

```python
def create_source_tables(
    self,
    source: Source,
    streams: "Literal['*'] | list[str] | None" = None,
) -> None
```

</ApiSignature>

Create tables in the cache for the provided source if they do not exist already.

Tables are created based upon the Source's catalog.

**Args:**

- **`source`**: The source to create tables for.
- **`streams`**: Stream names to create tables for. If None, use the Source's selected_streams or "*" if neither is set. If "*", all available streams will be used.

</ApiMember>

#### `execute_sql` {#airbyte.caches.base.CacheBase.execute_sql}

<ApiMember kind="method">

<ApiSignature>

```python
def execute_sql(self, sql: str | list[str]) -> None
```

</ApiSignature>

Execute one or more SQL statements against the cache's SQL backend.

If multiple SQL statements are given, they are executed in order,
within the same transaction.

This method is useful for creating tables, indexes, and other
schema objects in the cache. It does not return any results and it
automatically closes the connection after executing all statements.

This method is not intended for querying data. For that, use the `get_records`
method - or for a low-level interface, use the `get_sql_engine` method.

If any of the statements fail, the transaction is canceled and an exception
is raised. Most databases will rollback the transaction in this case.

</ApiMember>

#### `fetch_table_statistics` {#airbyte.caches.base.CacheBase.fetch_table_statistics}

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

Delegates to `self.processor.fetch_table_statistics()` which queries
row counts, column info, and per-column null/non-null stats for each
stream.

Returns a dict mapping stream name to a `TableStatistics` instance.
Streams whose tables are not found are omitted from the result.

</ApiMember>

#### `get_arrow_dataset` {#airbyte.caches.base.CacheBase.get_arrow_dataset}

<ApiMember kind="method">

<ApiSignature>

```python
def get_arrow_dataset(
    self,
    stream_name: str,
    *,
    max_chunk_size: int = 100000,
) -> pyarrow._dataset.Dataset
```

</ApiSignature>

Return an Arrow Dataset with the stream's data.

</ApiMember>

#### `get_pandas_dataframe` {#airbyte.caches.base.CacheBase.get_pandas_dataframe}

<ApiMember kind="method">

<ApiSignature>

```python
def get_pandas_dataframe(
    self,
    stream_name: str,
) -> pandas.core.frame.DataFrame
```

</ApiSignature>

Return a Pandas data frame with the stream's data.

</ApiMember>

#### `get_record_processor` {#airbyte.caches.base.CacheBase.get_record_processor}

<ApiMember kind="method">

<ApiSignature>

```python
def get_record_processor(
    self,
    source_name: str,
    catalog_provider: CatalogProvider,
    state_writer: StateWriterBase | None = None,
) -> SqlProcessorBase
```

</ApiSignature>

Return a record processor for the specified source name and catalog.

We first register the source and its catalog with the catalog manager. Then we create a new
SQL processor instance with (only) the given input catalog.

For the state writer, we use a state writer which stores state in an internal SQL table.

</ApiMember>

#### `get_records` {#airbyte.caches.base.CacheBase.get_records}

<ApiMember kind="method">

<ApiSignature>

```python
def get_records(self, stream_name: str) -> airbyte.datasets._sql.CachedDataset
```

</ApiSignature>

Uses SQLAlchemy to select all rows from the table.

</ApiMember>

#### `get_state_provider` {#airbyte.caches.base.CacheBase.get_state_provider}

<ApiMember kind="method">

<ApiSignature>

```python
def get_state_provider(
    self,
    source_name: str,
    *,
    refresh: bool = True,
    destination_name: str | None = None,
) -> StateProviderBase
```

</ApiSignature>

Return a state provider for the specified source name.

</ApiMember>

#### `get_state_writer` {#airbyte.caches.base.CacheBase.get_state_writer}

<ApiMember kind="method">

<ApiSignature>

```python
def get_state_writer(
    self,
    source_name: str,
    destination_name: str | None = None,
) -> StateWriterBase
```

</ApiSignature>

Return a state writer for the specified source name.

If syncing to the cache, `destination_name` should be `None`.
If syncing to a destination, `destination_name` should be the destination name.

</ApiMember>

#### `register_source` {#airbyte.caches.base.CacheBase.register_source}

<ApiMember kind="method">

<ApiSignature>

```python
def register_source(
    self,
    source_name: str,
    incoming_source_catalog: ConfiguredAirbyteCatalog,
    stream_names: set[str],
) -> None
```

</ApiSignature>

Register the source name and catalog.

</ApiMember>

#### `run_sql_query` {#airbyte.caches.base.CacheBase.run_sql_query}

<ApiMember kind="method">

<ApiSignature>

```python
def run_sql_query(
    self,
    sql_query: str,
    *,
    max_records: int | None = None,
) -> list[dict[str, typing.Any]]
```

</ApiSignature>

Run a SQL query against the cache and return results as a list of dictionaries.

This method is designed for single DML statements like SELECT, SHOW, or DESCRIBE.
For DDL statements or multiple statements, use the processor directly.

**Args:**

- **`sql_query`**: The SQL query to execute
- **`max_records`**: Maximum number of records to return. If None, returns all records.

**Returns:**

List of dictionaries representing the query results

</ApiMember>

</ApiMember>