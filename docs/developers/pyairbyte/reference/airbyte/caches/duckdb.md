---
id: airbyte-caches-duckdb
title: "airbyte.caches.duckdb Module"
sidebar_label: "airbyte.caches.duckdb"
---

# `airbyte.caches.duckdb` Module

A DuckDB implementation of the PyAirbyte cache.

## Usage Example

```python
from airbyte as ab
from airbyte.caches import DuckDBCache

cache = DuckDBCache(
    db_path="/path/to/my/duckdb-file",
    schema_name="myschema",
)
```

### `DuckDBCache` {#airbyte.caches.duckdb.DuckDBCache}

<ApiMember kind="class">

<ApiSignature>

```python
class DuckDBCache(**data: Any)
```

</ApiSignature>

A DuckDB cache.

Initialize the cache and backends.

**Bases:** `airbyte._processors.sql.duckdb.DuckDBConfig`, `airbyte.caches.base.CacheBase`, `airbyte.shared.sql_processor.SqlConfig`, `airbyte._writers.base.AirbyteWriterInterface`, `abc.ABC`

**Subclasses:** `airbyte.caches.motherduck.MotherDuckCache`

#### Attributes {#airbyte.caches.duckdb.DuckDBCache--attributes}

- **`paired_destination_config_class`**&nbsp;(`ClassVar[type | None]`)

  DestinationDuckdb(destination_path: 'str', DESTINATION_TYPE: 'Final[Duckdb]' = &lt;Duckdb.DUCKDB: 'duckdb'&gt;, motherduck_api_key: 'Optional[str]' = None, schema: 'Optional[str]' = None)

- **`paired_destination_name`**&nbsp;(`ClassVar[str | None]`)

</ApiMember>

### `DuckDBConfig` {#airbyte.caches.duckdb.DuckDBConfig}

<ApiMember kind="class">

<ApiSignature>

```python
class DuckDBConfig(**data: Any)
```

</ApiSignature>

Configuration for DuckDB.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

**Bases:** `airbyte.shared.sql_processor.SqlConfig`, `abc.ABC`

**Subclasses:** `airbyte.caches.duckdb.DuckDBCache`, `airbyte.caches.motherduck.MotherDuckConfig`

#### Attributes {#airbyte.caches.duckdb.DuckDBConfig--attributes}

- **`db_path`**&nbsp;(`Path | str`)

  Normally db_path is a Path object.

  The database name will be inferred from the file name. For example, given a `db_path` of
  `/path/to/my/duckdb-file`, the database name is `my_db`.

#### `get_sql_alchemy_url` {#airbyte.caches.duckdb.DuckDBConfig.get_sql_alchemy_url}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_alchemy_url(self) -> airbyte.secrets.base.SecretString
```

</ApiSignature>

Return the SQLAlchemy URL to use.

</ApiMember>

#### `get_sql_engine` {#airbyte.caches.duckdb.DuckDBConfig.get_sql_engine}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_engine(self) -> Engine
```

</ApiSignature>

Return the SQL Alchemy engine.

This method is overridden to ensure that the database parent directory is created if it
doesn't exist.

</ApiMember>

</ApiMember>