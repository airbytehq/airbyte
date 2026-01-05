---
sidebar_label: bigquery
title: airbyte._processors.sql.bigquery
---

A BigQuery implementation of the SQL Processor.

## annotations

## warnings

## Path

## TYPE\_CHECKING

## cast

## final

## auth

## oauth2

## sqlalchemy

## exc

## NotFound

## bigquery

## service\_account

## overrides

## Field

## sqlalchemy\_types

## make\_url

## exc

## JsonlWriter

## DEFAULT\_CACHE\_SCHEMA\_NAME

## SecretString

## SqlProcessorBase

## SqlConfig

## SQLTypeConverter

## BigQueryConfig Objects

```python
class BigQueryConfig(SqlConfig)
```

Configuration for BigQuery.

#### database\_name

The name of the project to use. In BigQuery, this is equivalent to the database name.

#### schema\_name

The name of the dataset to use. In BigQuery, this is equivalent to the schema name.

#### credentials\_path

The path to the credentials file to use.
If not passed, falls back to the default inferred from the environment.

#### dataset\_location

The geographic location of the BigQuery dataset (e.g., &#x27;US&#x27;, &#x27;EU&#x27;, etc.).
Defaults to &#x27;US&#x27;. See: https://cloud.google.com/bigquery/docs/locations

#### project\_name

```python
@property
def project_name() -> str
```

Return the project name (alias of self.database_name).

#### dataset\_name

```python
@property
def dataset_name() -> str
```

Return the dataset name (alias of self.schema_name).

#### get\_sql\_alchemy\_url

```python
@overrides
def get_sql_alchemy_url() -> SecretString
```

Return the SQLAlchemy URL to use.

We suppress warnings about unrecognized JSON type. More info on that here:
- https://github.com/airbytehq/PyAirbyte/issues/254

#### get\_database\_name

```python
@overrides
def get_database_name() -> str
```

Return the name of the database. For BigQuery, this is the project name.

#### get\_vendor\_client

```python
def get_vendor_client() -> bigquery.Client
```

Return a BigQuery python client.

## BigQueryTypeConverter Objects

```python
class BigQueryTypeConverter(SQLTypeConverter)
```

A class to convert types for BigQuery.

#### get\_string\_type

```python
@classmethod
def get_string_type(cls) -> sqlalchemy.types.TypeEngine
```

Return the string type for BigQuery.

#### to\_sql\_type

```python
@overrides
def to_sql_type(
    json_schema_property_def: dict[str, str | dict | list]
) -> sqlalchemy.types.TypeEngine
```

Convert a value to a SQL type.

We first call the parent class method to get the type. Then if the type is VARCHAR or
BIGINT, we replace it with respective BigQuery types.

## BigQuerySqlProcessor Objects

```python
class BigQuerySqlProcessor(SqlProcessorBase)
```

A BigQuery implementation of the SQL Processor.

#### file\_writer\_class

#### type\_converter\_class

#### supports\_merge\_insert

#### sql\_config

#### \_schema\_exists

#### \_fully\_qualified

```python
@final
@overrides
def _fully_qualified(table_name: str) -> str
```

Return the fully qualified name of the given table.

#### \_quote\_identifier

```python
@final
@overrides
def _quote_identifier(identifier: str) -> str
```

Return the identifier name.

BigQuery uses backticks to quote identifiers. Because BigQuery is case-sensitive for quoted
identifiers, we convert the identifier to lowercase before quoting it.

#### \_write\_files\_to\_new\_table

```python
def _write_files_to_new_table(files: list[Path], stream_name: str,
                              batch_id: str) -> str
```

Write a file(s) to a new table.

This is a generic implementation, which can be overridden by subclasses
to improve performance.

#### \_ensure\_schema\_exists

```python
def _ensure_schema_exists() -> None
```

Ensure the target schema exists.

We override the default implementation because BigQuery is very slow at scanning schemas.

This implementation simply calls &quot;CREATE SCHEMA IF NOT EXISTS&quot; and ignores any errors.

#### \_table\_exists

```python
def _table_exists(table_name: str) -> bool
```

Return true if the given table exists.

We override the default implementation because BigQuery is very slow at scanning tables.

#### \_get\_tables\_list

```python
@final
@overrides
def _get_tables_list() -> list[str]
```

Get the list of available tables in the schema.

For bigquery, {schema_name}.{table_name} is returned, so we need to
strip the schema name in front of the table name, if it exists.

Warning: This method is slow for BigQuery, as it needs to scan all tables in the dataset.
It has been observed to take 30+ seconds in some cases.

#### \_swap\_temp\_table\_with\_final\_table

```python
def _swap_temp_table_with_final_table(stream_name: str, temp_table_name: str,
                                      final_table_name: str) -> None
```

Swap the temp table with the main one, dropping the old version of the &#x27;final&#x27; table.

The BigQuery RENAME implementation requires that the table schema (dataset) is named in the
first part of the ALTER statement, but not in the second part.

For example, BigQuery expects this format:

ALTER TABLE my_schema.my_old_table_name RENAME TO my_new_table_name;

