---
id: airbyte-caches-generic
title: "airbyte.caches.generic Module"
sidebar_label: "airbyte.caches.generic"
toc_max_heading_level: 5
---

# `airbyte.caches.generic` Module

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

#### Bases {#airbyte.caches.generic.GenericSQLCacheConfig--bases}

`airbyte.caches.base.CacheBase`
#### Class Variables {#airbyte.caches.generic.GenericSQLCacheConfig--class-variables}

- **`sql_alchemy_url`**&nbsp;(`SecretString | str`)

</ApiMember>