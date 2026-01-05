---
sidebar_label: hashing
title: airbyte._util.hashing
---

Hashing utils for PyAirbyte.

## annotations

## hashlib

## Mapping

#### HASH\_SEED

Additional seed for randomizing one-way hashed strings.

#### one\_way\_hash

```python
def one_way_hash(obj: Mapping | list | object) -> str
```

Return a one-way hash of the given string.

To ensure a unique domain of hashes, we prepend a seed to the string before hashing.

