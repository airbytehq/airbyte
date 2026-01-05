---
sidebar_label: motherduck
title: airbyte._processors.sql.motherduck
---

A MotherDuck implementation of the cache, built on the DuckDB implementation.

## annotations

## warnings

## TYPE\_CHECKING

## DuckDBEngineWarning

## overrides

## DuckDBSqlProcessor

## JsonlWriter

## MotherDuckSqlProcessor Objects

```python
class MotherDuckSqlProcessor(DuckDBSqlProcessor)
```

A cache implementation for MotherDuck.

#### supports\_merge\_insert

#### file\_writer\_class

#### cache

#### \_setup

```python
@overrides
def _setup() -> None
```

Do any necessary setup, if applicable.

Note: The DuckDB parent class requires pre-creation of local directory structure. We
don&#x27;t need to do that here so we override the method be a no-op.

