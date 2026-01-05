---
sidebar_label: duckdb
title: airbyte._processors.sql.duckdb
---

A DuckDB implementation of the cache.

## annotations

## warnings

## Path

## dedent

## indent

## TYPE\_CHECKING

## Literal

## DuckDBEngineWarning

## overrides

## Field

## text

## JsonlWriter

## SecretString

## SqlProcessorBase

## SqlConfig

## DuckDBConfig Objects

```python
class DuckDBConfig(SqlConfig)
```

Configuration for DuckDB.

#### db\_path

Normally db_path is a Path object.

The database name will be inferred from the file name. For example, given a `db_path` of
`/path/to/my/duckdb-file`, the database name is `my_db`.

#### schema\_name

The name of the schema to write to. Defaults to &quot;main&quot;.

#### get\_sql\_alchemy\_url

```python
@overrides
def get_sql_alchemy_url() -> SecretString
```

Return the SQLAlchemy URL to use.

#### get\_database\_name

```python
@overrides
def get_database_name() -> str
```

Return the name of the database.

#### \_is\_file\_based\_db

```python
def _is_file_based_db() -> bool
```

Return whether the database is file-based.

#### get\_sql\_engine

```python
@overrides
def get_sql_engine() -> Engine
```

Return the SQL Alchemy engine.

This method is overridden to ensure that the database parent directory is created if it
doesn&#x27;t exist.

## DuckDBSqlProcessor Objects

```python
class DuckDBSqlProcessor(SqlProcessorBase)
```

A DuckDB implementation of the cache.

Jsonl is used for local file storage before bulk loading.
Unlike the Snowflake implementation, we can&#x27;t use the COPY command to load data
so we insert as values instead.

#### supports\_merge\_insert

#### file\_writer\_class

#### sql\_config

#### \_setup

```python
@overrides
def _setup() -> None
```

Create the database parent folder if it doesn&#x27;t yet exist.

#### \_write\_files\_to\_new\_table

```python
def _write_files_to_new_table(files: list[Path], stream_name: str,
                              batch_id: str) -> str
```

Write a file(s) to a new table.

We use DuckDB native SQL functions to efficiently read the files and insert
them into the table in a single operation.

#### \_do\_checkpoint

```python
def _do_checkpoint(connection: Connection | None = None) -> None
```

Checkpoint the given connection.

We override this method to ensure that the DuckDB WAL is checkpointed explicitly.
Otherwise DuckDB will lazily flush the WAL to disk, which can cause issues for users
who want to manipulate the DB files after writing them.

For more info:
- https://duckdb.org/docs/sql/statements/checkpoint.html

