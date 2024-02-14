# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Type conversion methods for SQL Caches."""
from __future__ import annotations

from typing import cast

import sqlalchemy
from rich import print


# Compare to documentation here: https://docs.airbyte.com/understanding-airbyte/supported-data-types
CONVERSION_MAP = {
    "string": sqlalchemy.types.VARCHAR,
    "integer": sqlalchemy.types.BIGINT,
    "number": sqlalchemy.types.DECIMAL,
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

    if json_schema_type in ["string", "number", "boolean", "integer"]:
        return cast(str, json_schema_type), None

    if json_schema_type == "object":
        return "object", None

    if json_schema_type == "array":
        items_def = json_schema_property_def.get("items", None)
        if isinstance(items_def, dict):
            subtype, _ = _get_airbyte_type(items_def)
            return "array", subtype

        return "array", None

    err_msg = f"Could not determine airbyte type from JSON schema type: {json_schema_property_def}"
    raise SQLTypeConversionError(err_msg)


class SQLTypeConverter:
    """A base class to perform type conversions."""

    def __init__(
        self,
        conversion_map: dict | None = None,
    ) -> None:
        self.conversion_map = conversion_map or CONVERSION_MAP

    @staticmethod
    def get_failover_type() -> sqlalchemy.types.TypeEngine:
        """Get the 'last resort' type to use if no other type is found."""
        return sqlalchemy.types.VARCHAR()

    def to_sql_type(
        self,
        json_schema_property_def: dict[str, str | dict | list],
    ) -> sqlalchemy.types.TypeEngine:
        """Convert a value to a SQL type."""
        try:
            airbyte_type, _ = _get_airbyte_type(json_schema_property_def)
            return self.conversion_map[airbyte_type]()
        except SQLTypeConversionError:
            print(f"Could not determine airbyte type from JSON schema: {json_schema_property_def}")
        except KeyError:
            print(f"Could not find SQL type for airbyte type: {airbyte_type}")

        json_schema_type = json_schema_property_def.get("type", None)
        json_schema_format = json_schema_property_def.get("format", None)

        if json_schema_type == "string" and json_schema_format == "date":
            return sqlalchemy.types.DATE()

        if json_schema_type == "string" and json_schema_format == "date-time":
            return sqlalchemy.types.TIMESTAMP()

        if json_schema_type == "array":
            # TODO: Implement array type conversion.
            return self.get_failover_type()

        if json_schema_type == "object":
            # TODO: Implement object type handling.
            return self.get_failover_type()

        return self.get_failover_type()
