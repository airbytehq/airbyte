# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mapping between SAP HANA SQL types, Airbyte JSON schema types and Python values."""

from __future__ import annotations

import base64
import datetime as dt
from collections.abc import Callable
from decimal import Decimal
from typing import Any


INTEGER_TYPES = frozenset({"TINYINT", "SMALLINT", "INTEGER", "BIGINT"})
DECIMAL_TYPES = frozenset({"DECIMAL", "SMALLDECIMAL"})
FLOAT_TYPES = frozenset({"REAL", "DOUBLE", "FLOAT"})
BOOLEAN_TYPES = frozenset({"BOOLEAN"})
DATE_TYPES = frozenset({"DATE", "DAYDATE"})
TIME_TYPES = frozenset({"TIME", "SECONDTIME"})
TIMESTAMP_TYPES = frozenset({"TIMESTAMP", "SECONDDATE", "LONGDATE"})
BINARY_TYPES = frozenset({"BINARY", "VARBINARY", "BLOB", "ST_GEOMETRY", "ST_POINT"})

# Types that can be used as an incremental cursor (must be totally ordered and comparable in SQL).
CURSOR_TYPES = (
    INTEGER_TYPES
    | DECIMAL_TYPES
    | FLOAT_TYPES
    | DATE_TYPES
    | TIME_TYPES
    | TIMESTAMP_TYPES
    | frozenset({"VARCHAR", "NVARCHAR", "ALPHANUM", "SHORTTEXT", "CHAR", "NCHAR"})
)


def json_schema_for(hana_type: str, decimal_as_string: bool = False) -> dict[str, Any]:
    """JSON schema of a nullable column of the given HANA type."""
    t = hana_type.upper()
    if t in INTEGER_TYPES:
        return {"type": ["null", "integer"]}
    if t in DECIMAL_TYPES:
        return {"type": ["null", "string"]} if decimal_as_string else {"type": ["null", "number"]}
    if t in FLOAT_TYPES:
        return {"type": ["null", "number"]}
    if t in BOOLEAN_TYPES:
        return {"type": ["null", "boolean"]}
    if t in DATE_TYPES:
        return {"type": ["null", "string"], "format": "date"}
    if t in TIME_TYPES:
        return {"type": ["null", "string"], "format": "time", "airbyte_type": "time_without_timezone"}
    if t in TIMESTAMP_TYPES:
        return {"type": ["null", "string"], "format": "date-time", "airbyte_type": "timestamp_without_timezone"}
    if t in BINARY_TYPES:
        return {"type": ["null", "string"], "contentEncoding": "base64"}
    # VARCHAR, NVARCHAR, ALPHANUM, SHORTTEXT, CHAR, NCHAR, CLOB, NCLOB, TEXT, BINTEXT and anything unknown.
    return {"type": ["null", "string"]}


class ValueConverter:
    """Converts values returned by hdbcli into JSON-serializable values matching json_schema_for()."""

    def __init__(self, decimal_as_string: bool = False, strip_nul_characters: bool = True):
        self.decimal_as_string = decimal_as_string
        self.strip_nul_characters = strip_nul_characters

    def __call__(self, value: Any) -> Any:
        if value is None or isinstance(value, (bool, int, float)):
            return value
        if isinstance(value, str):
            return value.replace("\x00", "") if self.strip_nul_characters else value
        if isinstance(value, Decimal):
            return self._decimal(value)
        # datetime must be checked before date (it is a subclass).
        if isinstance(value, dt.datetime):
            return value.isoformat()
        if isinstance(value, (dt.date, dt.time)):
            return value.isoformat()
        if isinstance(value, (bytes, bytearray, memoryview)):
            return base64.b64encode(bytes(value)).decode("ascii")
        read = getattr(value, "read", None)  # hdbcli LOB
        if callable(read):
            return self(read())
        return str(value)

    def _decimal(self, value: Decimal) -> Any:
        if self.decimal_as_string:
            return format(value, "f")
        if not value.is_finite():
            return None
        if value == value.to_integral_value():
            return int(value)
        return float(value)


def cursor_param_parser(hana_type: str) -> Callable[[Any], Any]:
    """Returns a function turning a serialized cursor value (from state) back into a bind parameter."""
    t = hana_type.upper()
    if t in INTEGER_TYPES:
        return int
    if t in DECIMAL_TYPES:
        return lambda v: Decimal(str(v))
    if t in FLOAT_TYPES:
        return float
    if t in DATE_TYPES:
        return lambda v: dt.date.fromisoformat(str(v))
    if t in TIME_TYPES:
        return lambda v: dt.time.fromisoformat(str(v))
    if t in TIMESTAMP_TYPES:
        return lambda v: dt.datetime.fromisoformat(str(v))
    return str
