---
sidebar_label: postgres
title: airbyte.caches.postgres
---

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

## annotations

## TYPE\_CHECKING

## ClassVar

## DestinationPostgres

## PostgresConfig

## PostgresSqlProcessor

## CacheBase

## postgres\_cache\_to\_destination\_configuration

## PostgresCache Objects

```python
class PostgresCache(PostgresConfig, CacheBase)
```

Configuration for the Postgres cache.

Also inherits config from the JsonlWriter, which is responsible for writing files to disk.

#### \_sql\_processor\_class

#### paired\_destination\_name

#### paired\_destination\_config\_class

#### paired\_destination\_config

```python
@property
def paired_destination_config() -> DestinationPostgres
```

Return a dictionary of destination configuration values.

#### clone\_as\_cloud\_destination\_config

```python
def clone_as_cloud_destination_config() -> DestinationPostgres
```

Return a DestinationPostgres instance with the same configuration.

#### \_\_all\_\_

