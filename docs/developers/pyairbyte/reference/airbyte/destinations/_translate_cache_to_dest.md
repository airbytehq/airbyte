---
sidebar_label: _translate_cache_to_dest
title: airbyte.destinations._translate_cache_to_dest
---

Cloud destinations for Airbyte.

## annotations

## Path

## TYPE\_CHECKING

## Any

## BatchedStandardInserts

## DatasetLocation

## DestinationBigquery

## DestinationDuckdb

## DestinationPostgres

## DestinationSnowflake

## UsernameAndPassword

## SecretString

#### SNOWFLAKE\_PASSWORD\_SECRET\_NAME

#### cache\_to\_destination\_configuration

```python
def cache_to_destination_configuration(
        cache: CacheBase) -> api_util.DestinationConfiguration
```

Get the destination configuration from the cache.

#### duckdb\_cache\_to\_destination\_configuration

```python
def duckdb_cache_to_destination_configuration(
        cache: DuckDBCache) -> DestinationDuckdb
```

Get the destination configuration from the DuckDB cache.

#### motherduck\_cache\_to\_destination\_configuration

```python
def motherduck_cache_to_destination_configuration(
        cache: MotherDuckCache) -> DestinationDuckdb
```

Get the destination configuration from the DuckDB cache.

#### postgres\_cache\_to\_destination\_configuration

```python
def postgres_cache_to_destination_configuration(
        cache: PostgresCache) -> DestinationPostgres
```

Get the destination configuration from the Postgres cache.

#### snowflake\_cache\_to\_destination\_configuration

```python
def snowflake_cache_to_destination_configuration(
        cache: SnowflakeCache) -> DestinationSnowflake
```

Get the destination configuration from the Snowflake cache.

#### bigquery\_cache\_to\_destination\_configuration

```python
def bigquery_cache_to_destination_configuration(
        cache: BigQueryCache) -> DestinationBigquery
```

Get the destination configuration from the BigQuery cache.

