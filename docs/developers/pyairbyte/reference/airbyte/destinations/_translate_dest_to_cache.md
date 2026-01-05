---
sidebar_label: _translate_dest_to_cache
title: airbyte.destinations._translate_dest_to_cache
---

Cloud destinations for Airbyte.

## annotations

## TYPE\_CHECKING

## Any

## DestinationBigquery

## DestinationDuckdb

## DestinationPostgres

## DestinationSnowflake

## CacheBase

## BigQueryCache

## DuckDBCache

## MotherDuckCache

## PostgresCache

## SnowflakeCache

## PyAirbyteSecretNotFoundError

## get\_secret

## SecretString

#### SNOWFLAKE\_PASSWORD\_SECRET\_NAME

#### destination\_to\_cache

```python
def destination_to_cache(
    destination_configuration: api_util.DestinationConfiguration
    | dict[str, Any]
) -> CacheBase
```

Get the destination configuration from the cache.

#### bigquery\_destination\_to\_cache

```python
def bigquery_destination_to_cache(
    destination_configuration: DestinationBigquery | dict[str, Any]
) -> BigQueryCache
```

Create a new BigQuery cache from the destination configuration.

We may have to inject credentials, because they are obfuscated when config
is returned from the REST API.

#### duckdb\_destination\_to\_cache

```python
def duckdb_destination_to_cache(
        destination_configuration: DestinationDuckdb) -> DuckDBCache
```

Create a new DuckDB cache from the destination configuration.

#### motherduck\_destination\_to\_cache

```python
def motherduck_destination_to_cache(
        destination_configuration: DestinationDuckdb) -> MotherDuckCache
```

Create a new DuckDB cache from the destination configuration.

#### postgres\_destination\_to\_cache

```python
def postgres_destination_to_cache(
        destination_configuration: DestinationPostgres) -> PostgresCache
```

Create a new Postgres cache from the destination configuration.

#### snowflake\_destination\_to\_cache

```python
def snowflake_destination_to_cache(
    destination_configuration: DestinationSnowflake | dict[str, Any],
    password_secret_name: str = SNOWFLAKE_PASSWORD_SECRET_NAME
) -> SnowflakeCache
```

Create a new Snowflake cache from the destination configuration.

We may have to inject credentials, because they are obfuscated when config
is returned from the REST API.

