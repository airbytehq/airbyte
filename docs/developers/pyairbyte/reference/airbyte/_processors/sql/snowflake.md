---
sidebar_label: snowflake
title: airbyte._processors.sql.snowflake
---

A Snowflake implementation of the SQL processor.

## annotations

## ThreadPoolExecutor

## Path

## indent

## TYPE\_CHECKING

## Any

## sqlalchemy

## default\_backend

## serialization

## overrides

## Field

## connector

## URL

## VARIANT

## text

## exc

## JsonlWriter

## DEFAULT\_CACHE\_SCHEMA\_NAME

## SecretString

## SqlProcessorBase

## SqlConfig

## SQLTypeConverter

#### MAX\_UPLOAD\_THREADS

## SnowflakeConfig Objects

```python
class SnowflakeConfig(SqlConfig)
```

Configuration for the Snowflake cache.

#### account

#### username

#### password

#### private\_key

#### private\_key\_path

#### private\_key\_passphrase

#### warehouse

#### database

#### role

#### schema\_name

#### data\_retention\_time\_in\_days

#### \_validate\_authentication\_config

```python
def _validate_authentication_config() -> None
```

Validate that authentication configuration is correct.

#### \_get\_private\_key\_content

```python
def _get_private_key_content() -> bytes
```

Get the private key content from either private_key or private_key_path.

#### \_get\_private\_key\_bytes

```python
def _get_private_key_bytes() -> bytes
```

#### get\_sql\_alchemy\_connect\_args

```python
@overrides
def get_sql_alchemy_connect_args() -> dict[str, Any]
```

Return the SQL Alchemy connect_args.

#### get\_create\_table\_extra\_clauses

```python
@overrides
def get_create_table_extra_clauses() -> list[str]
```

Return a list of clauses to append on CREATE TABLE statements.

#### get\_database\_name

```python
@overrides
def get_database_name() -> str
```

Return the name of the database.

#### get\_sql\_alchemy\_url

```python
@overrides
def get_sql_alchemy_url() -> SecretString
```

Return the SQLAlchemy URL to use.

#### get\_vendor\_client

```python
def get_vendor_client() -> object
```

Return the Snowflake connection object.

## SnowflakeTypeConverter Objects

```python
class SnowflakeTypeConverter(SQLTypeConverter)
```

A class to convert types for Snowflake.

#### to\_sql\_type

```python
@overrides
def to_sql_type(
    json_schema_property_def: dict[str, str | dict | list]
) -> sqlalchemy.types.TypeEngine
```

Convert a value to a SQL type.

We first call the parent class method to get the type. Then if the type JSON, we
replace it with VARIANT.

#### get\_json\_type

```python
@staticmethod
def get_json_type() -> sqlalchemy.types.TypeEngine
```

Get the type to use for nested JSON data.

## SnowflakeSqlProcessor Objects

```python
class SnowflakeSqlProcessor(SqlProcessorBase)
```

A Snowflake implementation of the cache.

#### file\_writer\_class

#### type\_converter\_class

#### supports\_merge\_insert

#### sql\_config

#### \_write\_files\_to\_new\_table

```python
@overrides
def _write_files_to_new_table(files: list[Path], stream_name: str,
                              batch_id: str) -> str
```

Write files to a new table.

#### \_init\_connection\_settings

```python
@overrides
def _init_connection_settings(connection: Connection) -> None
```

We set Snowflake-specific settings for the session.

This sets QUOTED_IDENTIFIERS_IGNORE_CASE setting to True, which is necessary because
Snowflake otherwise will treat quoted table and column references as case-sensitive.
More info: https://docs.snowflake.com/en/sql-reference/identifiers-syntax

This also sets MULTI_STATEMENT_COUNT to 0, which allows multi-statement commands.

