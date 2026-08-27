---
id: airbyte-caches-postgres
title: "airbyte.caches.postgres Module"
sidebar_label: "airbyte.caches.postgres"
toc_max_heading_level: 5
---

# `airbyte.caches.postgres` Module

A Postgres implementation of the PyAirbyte cache.

## Usage Example

```python
from airbyte as ab
from airbyte.caches import PostgresCache

cache = PostgresCache(
    host="myhost",
    port=5432,
    username="myusername",
    password=ab.get_secret("POSTGRES_PASSWORD"),
    database="mydatabase",
)
```

### `PostgresCache` {#airbyte.caches.postgres.PostgresCache}

<ApiMember kind="class">

<ApiSignature>

```python
class PostgresCache(**data: Any)
```

</ApiSignature>

Configuration for the Postgres cache.

Also inherits config from the JsonlWriter, which is responsible for writing files to disk.

Initialize the cache and backends.

#### Bases {#airbyte.caches.postgres.PostgresCache--bases}

`airbyte._processors.sql.postgres.PostgresConfig`, `airbyte.caches.base.CacheBase`
#### Class Variables {#airbyte.caches.postgres.PostgresCache--class-variables}

- **`paired_destination_config_class`**&nbsp;(`ClassVar[type | None]`)

  DestinationPostgres(database: 'str', host: 'str', username: 'str', DESTINATION_TYPE: 'Final[Postgres]' = &lt;Postgres.POSTGRES: 'postgres'&gt;, disable_type_dedupe: 'Optional[bool]' = False, drop_cascade: 'Optional[bool]' = False, jdbc_url_params: 'Optional[str]' = None, password: 'Optional[str]' = None, port: 'Optional[int]' = 5432, raw_data_schema: 'Optional[str]' = None, schema: 'Optional[str]' = 'public', ssl: 'Optional[bool]' = False, ssl_mode: 'Optional[SSLModes]' = None, tunnel_method: 'Optional[DestinationPostgresSSHTunnelMethod]' = None, unconstrained_number: 'Optional[bool]' = False)

- **`paired_destination_name`**&nbsp;(`ClassVar[str | None]`)

#### Methods {#airbyte.caches.postgres.PostgresCache--methods}

#### `clone_as_cloud_destination_config` {#airbyte.caches.postgres.PostgresCache.clone_as_cloud_destination_config}

<ApiMember kind="method">

<ApiSignature>

```python
def clone_as_cloud_destination_config(
    self,
) -> airbyte_api.models.destination_postgres.DestinationPostgres
```

</ApiSignature>

Return a DestinationPostgres instance with the same configuration.

</ApiMember>

</ApiMember>

### `PostgresConfig` {#airbyte.caches.postgres.PostgresConfig}

<ApiMember kind="class">

<ApiSignature>

```python
class PostgresConfig(**data: Any)
```

</ApiSignature>

Configuration for the Postgres cache.

Also inherits config from the JsonlWriter, which is responsible for writing files to disk.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Bases {#airbyte.caches.postgres.PostgresConfig--bases}

`airbyte.shared.sql_processor.SqlConfig`
#### Descendants {#airbyte.caches.postgres.PostgresConfig--descendants}

`airbyte.caches.postgres.PostgresCache`
#### Class Variables {#airbyte.caches.postgres.PostgresConfig--class-variables}

- **`database`**&nbsp;(`str`)

- **`host`**&nbsp;(`str`)

- **`password`**&nbsp;(`SecretString | str`)

- **`port`**&nbsp;(`int`)

- **`username`**&nbsp;(`str`)

#### Methods {#airbyte.caches.postgres.PostgresConfig--methods}

#### `get_sql_alchemy_url` {#airbyte.caches.postgres.PostgresConfig.get_sql_alchemy_url}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_alchemy_url(self) -> airbyte.secrets.base.SecretString
```

</ApiSignature>

Return the SQLAlchemy URL to use.

</ApiMember>

</ApiMember>