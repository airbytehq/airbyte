---
id: airbyte-types
title: "airbyte.types Module"
sidebar_label: "airbyte.types"
toc_max_heading_level: 5
---

# `airbyte.types` Module

Type conversion methods for SQL Caches.

### `SQLTypeConversionError` {#airbyte.types.SQLTypeConversionError}

<ApiMember kind="class">

<ApiSignature>

```python
class SQLTypeConversionError(*args, **kwargs)
```

</ApiSignature>

An exception to be raised when a type conversion fails.

#### Bases {#airbyte.types.SQLTypeConversionError--bases}

`builtins.Exception`

</ApiMember>

### `SQLTypeConverter` {#airbyte.types.SQLTypeConverter}

<ApiMember kind="class">

<ApiSignature>

```python
class SQLTypeConverter(conversion_map: dict | None = None)
```

</ApiSignature>

A base class to perform type conversions.

Initialize the type converter.

#### Descendants {#airbyte.types.SQLTypeConverter--descendants}

`airbyte._processors.sql.bigquery.BigQueryTypeConverter`, `airbyte._processors.sql.snowflake.SnowflakeTypeConverter`
#### Static Methods {#airbyte.types.SQLTypeConverter--static-methods}

#### `get_failover_type` {#airbyte.types.SQLTypeConverter.get_failover_type}

<ApiMember kind="method">

<ApiSignature>

```python
def get_failover_type() -> sqlalchemy.sql.type_api.TypeEngine
```

</ApiSignature>

Get the 'last resort' type to use if no other type is found.

</ApiMember>

#### `get_json_type` {#airbyte.types.SQLTypeConverter.get_json_type}

<ApiMember kind="method">

<ApiSignature>

```python
def get_json_type() -> sqlalchemy.sql.type_api.TypeEngine
```

</ApiSignature>

Get the type to use for nested JSON data.

</ApiMember>

#### `get_string_type` {#airbyte.types.SQLTypeConverter.get_string_type}

<ApiMember kind="method">

<ApiSignature>

```python
def get_string_type() -> sqlalchemy.sql.type_api.TypeEngine
```

</ApiSignature>

Get the type to use for string data.

</ApiMember>

#### Methods {#airbyte.types.SQLTypeConverter--methods}

#### `to_sql_type` {#airbyte.types.SQLTypeConverter.to_sql_type}

<ApiMember kind="method">

<ApiSignature>

```python
def to_sql_type(
    self,
    json_schema_property_def: dict[str, str | dict | list],
) -> sqlalchemy.sql.type_api.TypeEngine
```

</ApiSignature>

Convert a value to a SQL type.

</ApiMember>

</ApiMember>