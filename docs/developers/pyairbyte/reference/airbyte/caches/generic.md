---
id: airbyte-caches-generic
title: airbyte.caches.generic
---

Module airbyte.caches.generic
=============================
A Generic SQL Cache implementation.

Classes
-------

`GenericSQLCacheConfig(**data: Any)`
:   Allows configuring 'sql_alchemy_url' directly.
    
    Initialize the cache and backends.

    ### Ancestors (in MRO)

    * airbyte.caches.base.CacheBase
    * airbyte.shared.sql_processor.SqlConfig
    * pydantic.main.BaseModel
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Class variables

    `model_config`
    :

    `sql_alchemy_url: SecretString | str`
    :