---
sidebar_label: motherduck
title: airbyte.caches.motherduck
---

A MotherDuck implementation of the PyAirbyte cache, built on DuckDB.

## Usage Example

```python
from airbyte as ab
from airbyte.caches import MotherDuckCache

cache = MotherDuckCache(
    database=&quot;mydatabase&quot;,
    schema_name=&quot;myschema&quot;,
    api_key=ab.get_secret(&quot;MOTHERDUCK_API_KEY&quot;),
)

## annotations

## warnings

## TYPE\_CHECKING

## ClassVar

## DestinationDuckdb

## DuckDBEngineWarning

## overrides

## Field

## DuckDBConfig

## MotherDuckSqlProcessor

## DuckDBCache

## motherduck\_cache\_to\_destination\_configuration

## SecretString

## MotherDuckConfig Objects

```python
class MotherDuckConfig(DuckDBConfig)
```

Configuration for the MotherDuck cache.

#### database

#### api\_key

#### db\_path

pyrefly: ignore[bad-override]

#### \_paired\_destination\_name

#### get\_sql\_alchemy\_url

```python
@overrides
def get_sql_alchemy_url() -> SecretString
```

Return the SQLAlchemy URL to use.

#### get\_database\_name

```python
@overrides
def get_database_name() -> str
```

Return the name of the database.

## MotherDuckCache Objects

```python
class MotherDuckCache(MotherDuckConfig, DuckDBCache)
```

Cache that uses MotherDuck for external persistent storage.

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

