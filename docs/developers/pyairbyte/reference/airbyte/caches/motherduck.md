---
id: airbyte-caches-motherduck
title: "airbyte.caches.motherduck Module"
sidebar_label: "airbyte.caches.motherduck"
---

# `airbyte.caches.motherduck` Module

A MotherDuck implementation of the PyAirbyte cache, built on DuckDB.

## Usage Example

```python
from airbyte as ab
from airbyte.caches import MotherDuckCache

cache = MotherDuckCache(
    database="mydatabase",
    schema_name="myschema",
    api_key=ab.get_secret("MOTHERDUCK_API_KEY"),
)
```

### `MotherDuckCache` {#airbyte.caches.motherduck.MotherDuckCache}

<ApiMember kind="class">

<ApiSignature>

```python
class MotherDuckCache(**data: Any)
```

</ApiSignature>

Cache that uses MotherDuck for external persistent storage.

Initialize the cache and backends.

**Bases:** `airbyte.caches.motherduck.MotherDuckConfig`, `airbyte.caches.duckdb.DuckDBCache`, `airbyte._processors.sql.duckdb.DuckDBConfig`, `airbyte.caches.base.CacheBase`, `airbyte.shared.sql_processor.SqlConfig`, `airbyte._writers.base.AirbyteWriterInterface`, `abc.ABC`

#### Attributes {#airbyte.caches.motherduck.MotherDuckCache--attributes}

- **`paired_destination_name`**&nbsp;(`ClassVar[str | None]`)

</ApiMember>

### `MotherDuckConfig` {#airbyte.caches.motherduck.MotherDuckConfig}

<ApiMember kind="class">

<ApiSignature>

```python
class MotherDuckConfig(**data: Any)
```

</ApiSignature>

Configuration for the MotherDuck cache.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

**Bases:** `airbyte._processors.sql.duckdb.DuckDBConfig`, `airbyte.shared.sql_processor.SqlConfig`, `abc.ABC`

**Subclasses:** `airbyte.caches.motherduck.MotherDuckCache`

#### Attributes {#airbyte.caches.motherduck.MotherDuckConfig--attributes}

- **`api_key`**&nbsp;(`SecretString`)

- **`database`**&nbsp;(`str`)

- **`db_path`**&nbsp;(`str`)

#### `get_sql_alchemy_url` {#airbyte.caches.motherduck.MotherDuckConfig.get_sql_alchemy_url}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_alchemy_url(self) -> airbyte.secrets.base.SecretString
```

</ApiSignature>

Return the SQLAlchemy URL to use.

</ApiMember>

</ApiMember>