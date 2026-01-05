---
sidebar_label: generic
title: airbyte.caches.generic
---

A Generic SQL Cache implementation.

## annotations

## overrides

## CacheBase

## SecretString

## GenericSQLCacheConfig Objects

```python
class GenericSQLCacheConfig(CacheBase)
```

Allows configuring &#x27;sql_alchemy_url&#x27; directly.

#### sql\_alchemy\_url

#### get\_sql\_alchemy\_url

```python
@overrides
def get_sql_alchemy_url() -> SecretString
```

Returns a SQL Alchemy URL.

