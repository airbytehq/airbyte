---
sidebar_label: postgres
title: airbyte._processors.sql.postgres
---

A Postgres implementation of the cache.

## annotations

## functools

## overrides

## LowerCaseNormalizer

## JsonlWriter

## SecretString

## SqlConfig

## SqlProcessorBase

## PostgresConfig Objects

```python
class PostgresConfig(SqlConfig)
```

Configuration for the Postgres cache.

Also inherits config from the JsonlWriter, which is responsible for writing files to disk.

#### host

#### port

#### database

#### username

#### password

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

## PostgresNormalizer Objects

```python
class PostgresNormalizer(LowerCaseNormalizer)
```

A name normalizer for Postgres.

Postgres has specific field name length limits:
- Tables names are limited to 63 characters.
- Column names are limited to 63 characters.

The postgres normalizer inherits from the default LowerCaseNormalizer class, and
additionally truncates column and table names to 63 characters.

#### normalize

```python
@staticmethod
@functools.cache
def normalize(name: str) -> str
```

Normalize the name, truncating to 63 characters.

## PostgresSqlProcessor Objects

```python
class PostgresSqlProcessor(SqlProcessorBase)
```

A Postgres implementation of the cache.

Jsonl is used for local file storage before bulk loading.
Unlike the Snowflake implementation, we can&#x27;t use the COPY command to load data
so we insert as values instead.

TODO: Add optimized bulk load path for Postgres. Could use an alternate file writer
or another import method. (Relatively low priority, since for now it works fine as-is.)

#### supports\_merge\_insert

#### file\_writer\_class

#### sql\_config

#### normalizer

A Postgres-specific name normalizer for table and column name normalization.

