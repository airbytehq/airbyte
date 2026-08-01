---
id: airbyte-caches-postgres
title: airbyte.caches.postgres
---

Module airbyte.caches.postgres
==============================
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

Classes
-------

`PostgresCache(**data: Any)`
:   Configuration for the Postgres cache.
    
    Also inherits config from the JsonlWriter, which is responsible for writing files to disk.
    
    Initialize the cache and backends.

    ### Ancestors (in MRO)

    * airbyte._processors.sql.postgres.PostgresConfig
    * airbyte.caches.base.CacheBase
    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Class variables

    `model_config`
    :

    `paired_destination_config_class: ClassVar[type | None]`
    :   DestinationPostgres(database: 'str', host: 'str', username: 'str', DESTINATION_TYPE: 'Final[Postgres]' = &lt;Postgres.POSTGRES: 'postgres'&gt;, disable_type_dedupe: 'Optional[bool]' = False, drop_cascade: 'Optional[bool]' = False, jdbc_url_params: 'Optional[str]' = None, password: 'Optional[str]' = None, port: 'Optional[int]' = 5432, raw_data_schema: 'Optional[str]' = None, schema: 'Optional[str]' = 'public', ssl: 'Optional[bool]' = False, ssl_mode: 'Optional[SSLModes]' = None, tunnel_method: 'Optional[DestinationPostgresSSHTunnelMethod]' = None, unconstrained_number: 'Optional[bool]' = False)

    `paired_destination_name: ClassVar[str | None]`
    :

    ### Methods

    `clone_as_cloud_destination_config(self) ‑> airbyte_api.models.destination_postgres.DestinationPostgres`
    :   Return a DestinationPostgres instance with the same configuration.

`PostgresConfig(**data: Any)`
:   Configuration for the Postgres cache.
    
    Also inherits config from the JsonlWriter, which is responsible for writing files to disk.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * abc.ABC

    ### Descendants

    * airbyte.caches.postgres.PostgresCache

    ### Class variables

    `database: str`
    :

    `host: str`
    :

    `model_config`
    :

    `password: SecretString | str`
    :

    `port: int`
    :

    `username: str`
    :

    ### Methods

    `get_sql_alchemy_url(self) ‑> airbyte.secrets.base.SecretString`
    :   Return the SQLAlchemy URL to use.