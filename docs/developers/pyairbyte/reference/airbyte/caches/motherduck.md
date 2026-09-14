---
id: airbyte-caches-motherduck
title: airbyte.caches.motherduck
---

Module airbyte.caches.motherduck
================================
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

Classes
-------

`MotherDuckCache(**data: Any)`
:   Cache that uses MotherDuck for external persistent storage.
    
    Initialize the cache and backends.

    ### Ancestors (in MRO)

    * airbyte.caches.motherduck.MotherDuckConfig
    * airbyte.caches.duckdb.DuckDBCache
    * airbyte._processors.sql.duckdb.DuckDBConfig
    * airbyte.caches.base.CacheBase
    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Class variables

    `model_config`
    :

    `paired_destination_name: ClassVar[str | None]`
    :

`MotherDuckConfig(**data: Any)`
:   Configuration for the MotherDuck cache.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte._processors.sql.duckdb.DuckDBConfig
    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * abc.ABC

    ### Descendants

    * airbyte.caches.motherduck.MotherDuckCache

    ### Class variables

    `api_key: SecretString`
    :

    `database: str`
    :

    `db_path: str`
    :

    `model_config`
    :

    ### Methods

    `get_sql_alchemy_url(self) ‑> airbyte.secrets.base.SecretString`
    :   Return the SQLAlchemy URL to use.