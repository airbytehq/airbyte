---
sidebar_label: base
title: airbyte.caches.base
---

SQL Cache implementation.

## annotations

## contextlib

## Path

## IO

## TYPE\_CHECKING

## Any

## ClassVar

## Literal

## final

## pd

## pa

## ds

## Field

## PrivateAttr

## sqlalchemy\_exc

## text

## Self

## ConfiguredAirbyteCatalog

## constants

## AirbyteWriterInterface

## CatalogBackendBase

## SqlCatalogBackend

## SqlStateBackend

## DEFAULT\_ARROW\_MAX\_CHUNK\_SIZE

## TEMP\_FILE\_CLEANUP

## CachedDataset

## CatalogProvider

## SqlConfig

## StdOutStateWriter

## CacheBase Objects

```python
class CacheBase(SqlConfig, AirbyteWriterInterface)
```

Base configuration for a cache.

Caches inherit from the matching `SqlConfig` class, which provides the SQL config settings
and basic connectivity to the SQL database.

The cache is responsible for managing the state of the data synced to the cache, including the
stream catalog and stream state. The cache also provides the mechanism to read and write data
to the SQL backend specified in the `SqlConfig` class.

#### cache\_dir

The directory to store the cache in.

#### cleanup

Whether to clean up the cache after use.

#### \_name

#### \_sql\_processor\_class

#### \_read\_processor

#### \_catalog\_backend

#### \_state\_backend

#### paired\_destination\_name

#### paired\_destination\_config\_class

#### paired\_destination\_config

```python
@property
def paired_destination_config() -> Any | dict[str, Any]
```

Return a dictionary of destination configuration values.

#### \_\_init\_\_

```python
def __init__(**data: Any) -> None
```

Initialize the cache and backends.

#### close

```python
def close() -> None
```

Close all database connections and dispose of connection pools.

This method ensures that all SQLAlchemy engines created by this cache
and its processors are properly disposed, releasing all database connections.
This is especially important for file-based databases like DuckDB, which
lock the database file until all connections are closed.

This method is idempotent and can be called multiple times safely.

**Raises**:

- `Exception` - If any engine disposal fails, the exception will propagate
  to the caller. This ensures callers are aware of cleanup failures.

#### \_\_enter\_\_

```python
def __enter__() -> Self
```

Enter context manager.

#### \_\_exit\_\_

```python
def __exit__(exc_type: type[BaseException] | None,
             exc_val: BaseException | None,
             exc_tb: TracebackType | None) -> None
```

Exit context manager and clean up resources.

#### \_\_del\_\_

```python
def __del__() -> None
```

Clean up resources when cache is garbage collected.

#### config\_hash

```python
@property
def config_hash() -> str | None
```

Return a hash of the cache configuration.

This is the same as the SQLConfig hash from the superclass.

#### execute\_sql

```python
def execute_sql(sql: str | list[str]) -> None
```

Execute one or more SQL statements against the cache&#x27;s SQL backend.

If multiple SQL statements are given, they are executed in order,
within the same transaction.

This method is useful for creating tables, indexes, and other
schema objects in the cache. It does not return any results and it
automatically closes the connection after executing all statements.

This method is not intended for querying data. For that, use the `get_records`
method - or for a low-level interface, use the `get_sql_engine` method.

If any of the statements fail, the transaction is canceled and an exception
is raised. Most databases will rollback the transaction in this case.

#### processor

```python
@final
@property
def processor() -> SqlProcessorBase
```

Return the SQL processor instance.

#### run\_sql\_query

```python
def run_sql_query(sql_query: str,
                  *,
                  max_records: int | None = None) -> list[dict[str, Any]]
```

Run a SQL query against the cache and return results as a list of dictionaries.

This method is designed for single DML statements like SELECT, SHOW, or DESCRIBE.
For DDL statements or multiple statements, use the processor directly.

**Arguments**:

- `sql_query` - The SQL query to execute
- `max_records` - Maximum number of records to return. If None, returns all records.
  

**Returns**:

  List of dictionaries representing the query results

#### get\_record\_processor

```python
def get_record_processor(
        source_name: str,
        catalog_provider: CatalogProvider,
        state_writer: StateWriterBase | None = None) -> SqlProcessorBase
```

Return a record processor for the specified source name and catalog.

We first register the source and its catalog with the catalog manager. Then we create a new
SQL processor instance with (only) the given input catalog.

For the state writer, we use a state writer which stores state in an internal SQL table.

#### get\_records

```python
def get_records(stream_name: str) -> CachedDataset
```

Uses SQLAlchemy to select all rows from the table.

#### get\_pandas\_dataframe

```python
def get_pandas_dataframe(stream_name: str) -> pd.DataFrame
```

Return a Pandas data frame with the stream&#x27;s data.

#### get\_arrow\_dataset

```python
def get_arrow_dataset(
        stream_name: str,
        *,
        max_chunk_size: int = DEFAULT_ARROW_MAX_CHUNK_SIZE) -> ds.Dataset
```

Return an Arrow Dataset with the stream&#x27;s data.

#### streams

```python
@final
@property
def streams() -> dict[str, CachedDataset]
```

Return a temporary table name.

#### \_\_len\_\_

```python
@final
def __len__() -> int
```

Gets the number of streams.

#### \_\_bool\_\_

```python
@final
def __bool__() -> bool
```

Always True.

This is needed so that caches with zero streams are not falsey (None-like).

#### get\_state\_provider

```python
def get_state_provider(
        source_name: str,
        *,
        refresh: bool = True,
        destination_name: str | None = None) -> StateProviderBase
```

Return a state provider for the specified source name.

#### get\_state\_writer

```python
def get_state_writer(source_name: str,
                     destination_name: str | None = None) -> StateWriterBase
```

Return a state writer for the specified source name.

If syncing to the cache, `destination_name` should be `None`.
If syncing to a destination, `destination_name` should be the destination name.

#### register\_source

```python
def register_source(source_name: str,
                    incoming_source_catalog: ConfiguredAirbyteCatalog,
                    stream_names: set[str]) -> None
```

Register the source name and catalog.

#### create\_source\_tables

```python
def create_source_tables(
        source: Source,
        streams: Literal["*"] | list[str] | None = None) -> None
```

Create tables in the cache for the provided source if they do not exist already.

Tables are created based upon the Source&#x27;s catalog.

**Arguments**:

- `source` - The source to create tables for.
- `streams` - Stream names to create tables for. If None, use the Source&#x27;s selected_streams
  or &quot;*&quot; if neither is set. If &quot;*&quot;, all available streams will be used.

#### \_\_getitem\_\_

```python
def __getitem__(stream: str) -> CachedDataset
```

Return a dataset by stream name.

#### \_\_contains\_\_

```python
def __contains__(stream: str) -> bool
```

Return whether a stream is in the cache.

#### \_\_iter\_\_

```python
def __iter__() -> Iterator[tuple[str, Any]]
```

Iterate over the streams in the cache.

#### \_write\_airbyte\_message\_stream

```python
def _write_airbyte_message_stream(stdin: IO[str] | AirbyteMessageIterator,
                                  *,
                                  catalog_provider: CatalogProvider,
                                  write_strategy: WriteStrategy,
                                  state_writer: StateWriterBase | None = None,
                                  progress_tracker: ProgressTracker) -> None
```

Read from the connector and write to the cache.

