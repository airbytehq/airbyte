---
id: airbyte-types
title: airbyte.types
---

Module airbyte.types
====================
Type conversion methods for SQL Caches.

Classes
-------

`SQLTypeConversionError(*args, **kwargs)`
:   An exception to be raised when a type conversion fails.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`SQLTypeConverter(conversion_map: dict | None = None)`
:   A base class to perform type conversions.
    
    Initialize the type converter.

    ### Descendants

    * airbyte._processors.sql.bigquery.BigQueryTypeConverter
    * airbyte._processors.sql.snowflake.SnowflakeTypeConverter

    ### Static methods

    `get_failover_type() ‑> sqlalchemy.sql.type_api.TypeEngine`
    :   Get the 'last resort' type to use if no other type is found.

    `get_json_type() ‑> sqlalchemy.sql.type_api.TypeEngine`
    :   Get the type to use for nested JSON data.

    `get_string_type() ‑> sqlalchemy.sql.type_api.TypeEngine`
    :   Get the type to use for string data.

    ### Methods

    `to_sql_type(self, json_schema_property_def: dict[str, str | dict | list]) ‑> sqlalchemy.sql.type_api.TypeEngine`
    :   Convert a value to a SQL type.