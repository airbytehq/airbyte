"""Type conversion methods for SQL Caches."""

from collections import defaultdict
from typing import Any

import sqlalchemy

# Compare to documentation here: https://docs.airbyte.com/understanding-airbyte/supported-data-types
CONVERSION_MAP = {
    "string": sqlalchemy.types.VARCHAR,
    "integer": sqlalchemy.types.BIGINT,
    "number": sqlalchemy.types.DECIMAL,
    "boolean": sqlalchemy.types.BOOLEAN,
    "date": sqlalchemy.types.DATE,
    "timestamp_with_timezone": sqlalchemy.types.TIMESTAMP_WITH_TIMEZONE,
    "timestamp_without_timezone": sqlalchemy.types.TIMESTAMP_WITHOUT_TIMEZONE,
    "time_with_timezone": sqlalchemy.types.TIME,
    "time_without_timezone": sqlalchemy.types.TIME,
    # Technically 'object' and 'array' as JSON Schema types, not airbyte types.
    # We include them here for completeness.
    "object": sqlalchemy.types.VARCHAR,
    "array": sqlalchemy.types.VARCHAR,
}


class SQLTypeConversionError(Exception):
    """An exception to be raised when a type conversion fails."""


class SQLTypeConverter:
    """A base class to perform type conversions."""

    def __init__(
        self,
        conversion_map: dict | None = None,
        **kwargs,  # Additional arguments (future proofing)
    ):
        self.conversion_map = defaultdict(
            self.get_failover_type,
            conversion_map or CONVERSION_MAP,
        )

    @staticmethod
    def get_failover_type() -> sqlalchemy.types.TypeEngine:
        """Get the 'last resort' type to use if no other type is found."""
        return sqlalchemy.types.VARCHAR()

    def to_sql_type(self, json_schema_property_def: dict[str, str | dict]) -> sqlalchemy.types.TypeEngine:
        """Convert a value to a SQL type."""
        try:
            airbyte_type = json_schema_property_def["airbyte_type"]
            json_schema_type = json_schema_property_def["type"]
        except KeyError as ex:
            raise SQLTypeConversionError(f"Invalid JSON schema: {json_schema_type}") from ex

        if json_schema_type == "array":
            # TODO: Implement array type conversion.
            return self.get_failover_type()

        if json_schema_type == "object":
            # TODO: Implement object type handling.
            return self.get_failover_type()

        return self.conversion_map[airbyte_type]()
