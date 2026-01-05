---
sidebar_label: duckdb
title: airbyte.caches.duckdb
---

A DuckDB implementation of the PyAirbyte cache.

## Usage Example

```python
from airbyte as ab
from airbyte.caches import DuckDBCache

cache = DuckDBCache(
    db_path="/path/to/my/duckdb-file",
    schema_name="myschema",
)
```

## annotations

## warnings

## TYPE\_CHECKING

## ClassVar

## DestinationDuckdb

## DuckDBEngineWarning

## DuckDBConfig

## DuckDBSqlProcessor

## CacheBase

## duckdb\_cache\_to\_destination\_configuration

## DuckDBCache Objects

```python
class DuckDBCache(DuckDBConfig, CacheBase)
```

A DuckDB cache.

#### \_sql\_processor\_class

#### paired\_destination\_name

#### paired\_destination\_config\_class

#### paired\_destination\_config

```python
@property
def paired_destination_config() -> DestinationDuckdb
```

Return a dictionary of destination configuration values.

#### \_\_all\_\_

