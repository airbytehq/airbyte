---
id: airbyte-caches-motherduck
title: "airbyte.caches.motherduck Module"
sidebar_label: "airbyte.caches.motherduck"
toc_max_heading_level: 5
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

#### Bases {#airbyte.caches.motherduck.MotherDuckCache--bases}

`airbyte.caches.motherduck.MotherDuckConfig`, `airbyte.caches.duckdb.DuckDBCache`
#### Class Variables {#airbyte.caches.motherduck.MotherDuckCache--class-variables}

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

#### Bases {#airbyte.caches.motherduck.MotherDuckConfig--bases}

`airbyte._processors.sql.duckdb.DuckDBConfig`
#### Descendants {#airbyte.caches.motherduck.MotherDuckConfig--descendants}

`airbyte.caches.motherduck.MotherDuckCache`
#### Class Variables {#airbyte.caches.motherduck.MotherDuckConfig--class-variables}

- **`api_key`**&nbsp;(`SecretString`)

- **`database`**&nbsp;(`str`)

- **`db_path`**&nbsp;(`str`)

#### Methods {#airbyte.caches.motherduck.MotherDuckConfig--methods}

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