---
id: airbyte-caches-generic
title: airbyte.caches.generic
---

A Generic SQL Cache implementation.

### `GenericSQLCacheConfig` {#airbyte.caches.generic.GenericSQLCacheConfig}

<ApiMember kind="class">

<ApiSignature>

```python
class GenericSQLCacheConfig(**data: Any)
```

</ApiSignature>

Allows configuring 'sql_alchemy_url' directly.

Initialize the cache and backends.

**Bases:** `airbyte.caches.base.CacheBase`, `airbyte.shared.sql_processor.SqlConfig`, `airbyte._writers.base.AirbyteWriterInterface`, `abc.ABC`

#### Attributes {#airbyte.caches.generic.GenericSQLCacheConfig--attributes}

- **`sql_alchemy_url`**&nbsp;(`SecretString | str`)

</ApiMember>