# noqa: A005  # Allow shadowing the built-in 'types' module
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Type conversion methods for SQL Caches."""

from __future__ import annotations

from typing import cast

import sqlalchemy
from rich import print  # noqa: A004  # Allow shadowing the built-in


# Compare to documentation here: https://docs.airbyte.com/understanding-airbyte/supported-data-types
CONVERSION_MAP = {
    "string": sqlalchemy.types.VARCHAR,
    "integer": sqlalchemy.types.BIGINT,
    "number": sqlalchemy.types.DECIMAL(38, 9),
    "boolean": sqlalchemy.types.BOOLEAN,
    "date": sqlalchemy.types.DATE,
    "timestamp_with_timezone": sqlalchemy.types.TIMESTAMP,
    "timestamp_without_timezone": sqlalchemy.types.TIMESTAMP,
    "time_with_timezone": sqlalchemy.types.TIME,
    "time_without_timezone": sqlalchemy.types.TIME,
    # Technically 'object' and 'array' as JSON Schema types, not airbyte types.
    # We include them here for completeness.
    "object": sqlalchemy.types.JSON,
    "array": sqlalchemy.types.JSON,
    "vector_array": sqlalchemy.types.ARRAY,
}


class SQLTypeConversionError(Exception):
    """An exception to be raised when a type conversion fails."""


def _get_airbyte_type(  # noqa: PLR0911  # Too many return statements
    json_schema_property_def: dict[str, str | dict | list],
) -> tuple[str, str | None]:
    """Get the airbyte type and subtype from a JSON schema property definition.

    Subtype is only used for array types. Otherwise, subtype will return None.
    """
    airbyte_type = cast(str, json_schema_property_def.get("airbyte_type", None))
    if airbyte_type:
        return airbyte_type, None

    json_schema_type = json_schema_property_def.get("type", None)
    json_schema_format = json_schema_property_def.get("format", None)

    # if json_schema_type is an array of two strings with one of them being null, pick the other one
    # this strategy is often used by connectors to indicate a field might not be set all the time
    if isinstance(json_schema_type, list):
        non_null_types = [t for t in json_schema_type if t != "null"]
        if len(non_null_types) == 1:
            json_schema_type = non_null_types[0]

    if json_schema_type == "string":
        if json_schema_format == "date":
            return "date", None

        if json_schema_format == "date-time":
            return "timestamp_with_timezone", None

        if json_schema_format == "time":
            return "time_without_timezone", None

    if isinstance(json_schema_type, str) and json_schema_type in {
        "string",
        "number",
        "boolean",
        "integer",
    }:
        return json_schema_type, None

    if json_schema_type == "object":
        return "object", None

    if json_schema_type == "array":
        items_def = json_schema_property_def.get("items", None)
        if isinstance(items_def, dict):
            try:
                subtype, _ = _get_airbyte_type(items_def)
            except SQLTypeConversionError:
                # We have enough information, so we can ignore parsing errors on subtype.
                subtype = None

            return "array", subtype

        return "array", None

    if json_schema_type == "vector_array":
        return "vector_array", "Float"

    err_msg = f"Could not determine airbyte type from JSON schema type: {json_schema_property_def}"
    raise SQLTypeConversionError(err_msg)


class SQLTypeConverter:
    """A base class to perform type conversions."""

    def __init__(
        self,
        conversion_map: dict | None = None,
    ) -> None:
        """Initialize the type converter."""
        self.conversion_map = conversion_map or CONVERSION_MAP

    @classmethod
    def get_string_type(cls) -> sqlalchemy.types.TypeEngine:
        """Get the type to use for string data."""
        return sqlalchemy.types.VARCHAR()

    @classmethod
    def get_failover_type(cls) -> sqlalchemy.types.TypeEngine:
        """Get the 'last resort' type to use if no other type is found."""
        return cls.get_string_type()

    @classmethod
    def get_json_type(cls) -> sqlalchemy.types.TypeEngine:
        """Get the type to use for nested JSON data."""
        return sqlalchemy.types.JSON()

    def to_sql_type(  # noqa: PLR0911  # Too many return statements
        self,
        json_schema_property_def: dict[str, str | dict | list],
    ) -> sqlalchemy.types.TypeEngine:
        """Convert a value to a SQL type."""
        try:
            airbyte_type, _ = _get_airbyte_type(json_schema_property_def)
            # to-do - is there a better way to check the following
            if airbyte_type == "vector_array":
                return sqlalchemy.types.ARRAY(sqlalchemy.types.Float())
            sql_type = self.conversion_map[airbyte_type]
        except SQLTypeConversionError:
            print(f"Could not determine airbyte type from JSON schema: {json_schema_property_def}")
        except KeyError:
            print(f"Could not find SQL type for airbyte type: {airbyte_type}")
        else:
            # No exceptions were raised, so we can return the SQL type.
            if isinstance(sql_type, type):
                # This is a class. Call its constructor.
                sql_type = sql_type()

            return sql_type

        json_schema_type = json_schema_property_def.get("type", None)
        json_schema_format = json_schema_property_def.get("format", None)

        if json_schema_type == "string" and json_schema_format == "date":
            return sqlalchemy.types.DATE()

        if json_schema_type == "string" and json_schema_format == "date-time":
            return sqlalchemy.types.TIMESTAMP()

        if json_schema_type == "array":
            return sqlalchemy.types.JSON()

        if json_schema_type == "object":
            return sqlalchemy.types.JSON()

        return self.get_failover_type()
