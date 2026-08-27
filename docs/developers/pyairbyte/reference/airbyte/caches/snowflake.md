---
id: airbyte-caches-snowflake
title: "airbyte.caches.snowflake Module"
sidebar_label: "airbyte.caches.snowflake"
toc_max_heading_level: 5
---

# `airbyte.caches.snowflake` Module

A Snowflake implementation of the PyAirbyte cache.

## Usage Example

### Password connection:

```python
from airbyte as ab
from airbyte.caches import SnowflakeCache

cache = SnowflakeCache(
    account="myaccount",
    username="myusername",
    password=ab.get_secret("SNOWFLAKE_PASSWORD"), # optional
    warehouse="mywarehouse",
    database="mydatabase",
    role="myrole",
    schema_name="myschema",
)
```

### Private key connection:

```python
from airbyte as ab
from airbyte.caches import SnowflakeCache

cache = SnowflakeCache(
    account="myaccount",
    username="myusername",
    private_key=ab.get_secret("SNOWFLAKE_PRIVATE_KEY"),
    private_key_passphrase=ab.get_secret("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"), # optional
    warehouse="mywarehouse",
    database="mydatabase",
    role="myrole",
    schema_name="myschema",
)
```

### Private key path connection:

```python
from airbyte as ab
from airbyte.caches import SnowflakeCache

cache = SnowflakeCache(
    account="myaccount",
    username="myusername",
    private_key_path="path/to/my/private_key.pem",
    private_key_passphrase=ab.get_secret("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"), # optional
    warehouse="mywarehouse",
    database="mydatabase",
    role="myrole",
    schema_name="myschema",
)
```

### `SnowflakeCache` {#airbyte.caches.snowflake.SnowflakeCache}

<ApiMember kind="class">

<ApiSignature>

```python
class SnowflakeCache(**data: Any)
```

</ApiSignature>

Configuration for the Snowflake cache.

Initialize the cache and backends.

#### Bases {#airbyte.caches.snowflake.SnowflakeCache--bases}

`airbyte._processors.sql.snowflake.SnowflakeConfig`, `airbyte.caches.base.CacheBase`
#### Class Variables {#airbyte.caches.snowflake.SnowflakeCache--class-variables}

- **`dedupe_mode`**&nbsp;(`RecordDedupeMode`)

- **`paired_destination_config_class`**&nbsp;(`ClassVar[type | None]`)

  DestinationSnowflake(database: 'str', host: 'str', role: 'str', schema: 'str', username: 'str', warehouse: 'str', credentials: 'Optional[AuthorizationMethod]' = None, DESTINATION_TYPE: 'Final[Snowflake]' = &lt;Snowflake.SNOWFLAKE: 'snowflake'&gt;, disable_type_dedupe: 'Optional[bool]' = False, jdbc_url_params: 'Optional[str]' = None, raw_data_schema: 'Optional[str]' = None, retention_period_days: 'Optional[int]' = 1, use_merge_for_upsert: 'Optional[bool]' = False)

- **`paired_destination_name`**&nbsp;(`ClassVar[str | None]`)

</ApiMember>

### `SnowflakeConfig` {#airbyte.caches.snowflake.SnowflakeConfig}

<ApiMember kind="class">

<ApiSignature>

```python
class SnowflakeConfig(**data: Any)
```

</ApiSignature>

Configuration for the Snowflake cache.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Bases {#airbyte.caches.snowflake.SnowflakeConfig--bases}

`airbyte.shared.sql_processor.SqlConfig`
#### Descendants {#airbyte.caches.snowflake.SnowflakeConfig--descendants}

`airbyte.caches.snowflake.SnowflakeCache`
#### Class Variables {#airbyte.caches.snowflake.SnowflakeConfig--class-variables}

- **`account`**&nbsp;(`str`)

- **`data_retention_time_in_days`**&nbsp;(`int | None`)

- **`database`**&nbsp;(`str`)

- **`password`**&nbsp;(`SecretString | None`)

- **`private_key`**&nbsp;(`SecretString | None`)

- **`private_key_passphrase`**&nbsp;(`SecretString | None`)

- **`private_key_path`**&nbsp;(`str | None`)

- **`role`**&nbsp;(`str`)

- **`username`**&nbsp;(`str`)

- **`warehouse`**&nbsp;(`str`)

#### Methods {#airbyte.caches.snowflake.SnowflakeConfig--methods}

#### `get_sql_alchemy_url` {#airbyte.caches.snowflake.SnowflakeConfig.get_sql_alchemy_url}

<ApiMember kind="method">

<ApiSignature>

```python
def get_sql_alchemy_url(self) -> airbyte.secrets.base.SecretString
```

</ApiSignature>

Return the SQLAlchemy URL to use.

</ApiMember>

#### `get_vendor_client` {#airbyte.caches.snowflake.SnowflakeConfig.get_vendor_client}

<ApiMember kind="method">

<ApiSignature>

```python
def get_vendor_client(self) -> object
```

</ApiSignature>

Return the Snowflake connection object.

</ApiMember>

</ApiMember>