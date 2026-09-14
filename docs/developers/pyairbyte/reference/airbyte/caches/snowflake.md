---
id: airbyte-caches-snowflake
title: airbyte.caches.snowflake
---

Module airbyte.caches.snowflake
===============================
A Snowflake implementation of the PyAirbyte cache.

## Usage Example

# Password connection:

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

# Private key connection:

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

# Private key path connection:

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

Classes
-------

`SnowflakeCache(**data: Any)`
:   Configuration for the Snowflake cache.
    
    Initialize the cache and backends.

    ### Ancestors (in MRO)

    * airbyte._processors.sql.snowflake.SnowflakeConfig
    * airbyte.caches.base.CacheBase
    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Class variables

    `dedupe_mode: RecordDedupeMode`
    :

    `model_config`
    :

    `paired_destination_config_class: ClassVar[type | None]`
    :   DestinationSnowflake(database: 'str', host: 'str', role: 'str', schema: 'str', username: 'str', warehouse: 'str', credentials: 'Optional[AuthorizationMethod]' = None, DESTINATION_TYPE: 'Final[Snowflake]' = &lt;Snowflake.SNOWFLAKE: 'snowflake'&gt;, disable_type_dedupe: 'Optional[bool]' = False, jdbc_url_params: 'Optional[str]' = None, raw_data_schema: 'Optional[str]' = None, retention_period_days: 'Optional[int]' = 1, use_merge_for_upsert: 'Optional[bool]' = False)

    `paired_destination_name: ClassVar[str | None]`
    :

`SnowflakeConfig(**data: Any)`
:   Configuration for the Snowflake cache.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * abc.ABC

    ### Descendants

    * airbyte.caches.snowflake.SnowflakeCache

    ### Class variables

    `account: str`
    :

    `data_retention_time_in_days: int | None`
    :

    `database: str`
    :

    `model_config`
    :

    `password: SecretString | None`
    :

    `private_key: SecretString | None`
    :

    `private_key_passphrase: SecretString | None`
    :

    `private_key_path: str | None`
    :

    `role: str`
    :

    `username: str`
    :

    `warehouse: str`
    :

    ### Methods

    `get_sql_alchemy_url(self) ‑> airbyte.secrets.base.SecretString`
    :   Return the SQLAlchemy URL to use.

    `get_vendor_client(self) ‑> object`
    :   Return the Snowflake connection object.