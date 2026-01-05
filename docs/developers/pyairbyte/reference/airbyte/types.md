---
sidebar_label: types
title: airbyte.types
---

Type conversion methods for SQL Caches.

## annotations

## cast

## sqlalchemy

## print

#### CONVERSION\_MAP

## SQLTypeConversionError Objects

```python
class SQLTypeConversionError(Exception)
```

An exception to be raised when a type conversion fails.

#### \_get\_airbyte\_type

```python
def _get_airbyte_type(
    json_schema_property_def: dict[str, str | dict | list]
) -> tuple[str, str | None]
```

Get the airbyte type and subtype from a JSON schema property definition.

Subtype is only used for array types. Otherwise, subtype will return None.

## SQLTypeConverter Objects

```python
class SQLTypeConverter()
```

A base class to perform type conversions.

#### \_\_init\_\_

```python
def __init__(conversion_map: dict | None = None) -> None
```

Initialize the type converter.

#### get\_string\_type

```python
@classmethod
def get_string_type(cls) -> sqlalchemy.types.TypeEngine
```

Get the type to use for string data.

#### get\_failover\_type

```python
@classmethod
def get_failover_type(cls) -> sqlalchemy.types.TypeEngine
```

Get the &#x27;last resort&#x27; type to use if no other type is found.

#### get\_json\_type

```python
@classmethod
def get_json_type(cls) -> sqlalchemy.types.TypeEngine
```

Get the type to use for nested JSON data.

#### to\_sql\_type

```python
def to_sql_type(
    json_schema_property_def: dict[str, str | dict | list]
) -> sqlalchemy.types.TypeEngine
```

Convert a value to a SQL type.

