"""
Type conversion utilities for converting Airbyte types to PyArrow types.

See: https://docs.airbyte.com/platform/understanding-airbyte/supported-data-types
"""

import json
from datetime import date, datetime, time
from typing import Any

import pyarrow as pa


def convert_to_arrow(value: Any, property_schema: dict) -> tuple[pa.DataType, Any]:
    """Convert an Airbyte value to PyArrow type and value.

    Args:
        value: The value to convert.
        property_schema: The Airbyte JSON schema for the property.

    Returns:
        A tuple of (PyArrow type, converted value).
    """
    json_type = property_schema.get("type")
    format_ = property_schema.get("format")
    airbyte_type = property_schema.get("airbyte_type")

    # Handle nullable types (e.g., ["null", "string"])
    if isinstance(json_type, list):
        json_type = next((t for t in json_type if t != "null"), "string")

    # Date: {"type": "string", "format": "date"}
    if json_type == "string" and format_ == "date":
        converted = parse_date(value)
        return pa.date32(), converted

    # Timestamp: {"type": "string", "format": "date-time"}
    if json_type == "string" and format_ == "date-time":
        converted = parse_timestamp(value)
        if airbyte_type == "timestamp_without_timezone":
            return pa.timestamp("us"), converted
        return pa.timestamp("us", tz="UTC"), converted

    # Time: {"type": "string", "format": "time"}
    if json_type == "string" and format_ == "time":
        converted = parse_time(value)
        return pa.time64("us"), converted

    # String
    if json_type == "string":
        return pa.string(), value

    # Integer
    if json_type == "integer":
        return pa.int64(), value

    # Number
    if json_type == "number":
        if airbyte_type == "integer":
            return pa.int64(), value
        return pa.float64(), value

    # Boolean
    if json_type == "boolean":
        return pa.bool_(), value

    # Default fallback - serialize complex types to JSON
    if isinstance(value, (dict, list)):
        return pa.string(), json.dumps(value)

    return pa.string(), value


def parse_date(value: Any) -> date | None:
    """Parse a date value from Airbyte format.

    Args:
        value: The value to parse. Can be None, a date, datetime, or string.

    Returns:
        A date object or None.
    """
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    # String format: "2021-01-23"
    return datetime.fromisoformat(str(value).replace(" BC", "")).date()


def parse_timestamp(value: Any) -> datetime | None:
    """Parse a timestamp value from Airbyte format.

    Args:
        value: The value to parse. Can be None, a datetime, or string.

    Returns:
        A datetime object or None.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    # String format: "2022-11-22T01:23:45.123456+05:00" or "2022-11-22T01:23:45Z"
    cleaned = str(value).replace(" BC", "")
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    return datetime.fromisoformat(cleaned)


def parse_time(value: Any) -> time | None:
    """Parse a time value from Airbyte format.

    Args:
        value: The value to parse. Can be None, a time, or string.

    Returns:
        A time object or None.
    """
    if value is None:
        return None
    if isinstance(value, time):
        return value
    # String format: "01:23:45.123456" or "01:23:45.123456+05:00"
    time_str = str(value).split("+")[0].split("Z")[0]
    # Handle negative timezone offset
    if "-" in time_str and time_str.count("-") > 0 and ":" in time_str.split("-")[-1]:
        time_str = "-".join(time_str.split("-")[:-1])
    fmt = "%H:%M:%S.%f" if "." in time_str else "%H:%M:%S"
    return datetime.strptime(time_str, fmt).time()
