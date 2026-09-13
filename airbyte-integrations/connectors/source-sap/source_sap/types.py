"""SAP/DDIC type mapping and orjson-safe value coercion.

Two jobs:

1. Turn the field metadata ERPL reports (``sap_describe_fields`` for RFC,
   the ``fields`` STRUCT of ``sap_odp_describe`` for ODP) into a JSON Schema.
2. Turn a DuckDB result row into something ``orjson`` can serialize.  DuckDB
   hands back ``Decimal``, ``date``, ``time``, ``datetime`` and ``bytes``; the
   CDK entrypoint silently falls back to ``json.dumps`` when orjson chokes on a
   value, which costs 5-10x throughput and logs a warning per sync.
"""

from __future__ import annotations

import base64
import datetime
import logging
from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal
from typing import Any

logger = logging.getLogger("airbyte")

_STRING: dict[str, Any] = {"type": ["null", "string"]}
_INTEGER: dict[str, Any] = {"type": ["null", "integer"]}
_NUMBER: dict[str, Any] = {"type": ["null", "number"]}
_DATE: dict[str, Any] = {"type": ["null", "string"], "format": "date"}
_TIME: dict[str, Any] = {"type": ["null", "string"], "format": "time"}
_DATETIME: dict[str, Any] = {"type": ["null", "string"], "format": "date-time"}
_BINARY: dict[str, Any] = {"type": ["null", "string"], "contentEncoding": "base64"}
# Exact numerics are emitted as decimal strings, so they need Airbyte's big_number
# hint to survive the destination without a float round trip.
_BIG_NUMBER: dict[str, Any] = {"type": ["null", "number"], "airbyte_type": "big_number"}

# Mirrors the SAP <-> DuckDB mapping documented in erpl's API_REFERENCE.md.
# fmt: off
_SAP_TYPES: dict[str, dict[str, Any]] = {
    # character-ish
    "CHAR": _STRING, "CLNT": _STRING, "LANG": _STRING, "CUKY": _STRING, "UNIT": _STRING,
    "STRING": _STRING, "STRG": _STRING, "SSTR": _STRING, "LCHR": _STRING, "XMLDATA": _STRING,
    # numeric-looking but must keep leading zeros
    "NUMC": _STRING, "ACCP": _STRING,
    # integers
    "INT1": _INTEGER, "INT2": _INTEGER, "INT4": _INTEGER, "INT8": _INTEGER, "PREC": _INTEGER,
    # floats
    "FLTP": _NUMBER,
    # exact numerics
    "DEC": _BIG_NUMBER, "CURR": _BIG_NUMBER, "QUAN": _BIG_NUMBER,
    "DECF16": _BIG_NUMBER, "DECF34": _BIG_NUMBER,
    # temporal
    "DATS": _DATE, "TIMS": _TIME,
    "UTCLONG": _DATETIME, "UTCL": _DATETIME, "UTCS": _DATETIME, "UTCM": _DATETIME,
    # binary
    "RAW": _BINARY, "LRAW": _BINARY, "RAWSTRING": _BINARY, "RSTR": _BINARY,
}
# fmt: on


def sap_type_to_json_schema(sap_type: str, length: int = 0, decimals: int = 0) -> dict[str, Any]:
    """Map one DDIC type to a JSON Schema fragment.

    Unknown types degrade to string with a warning.  Raising here (what the
    previous connector did) makes ``discover`` fail outright on any table that
    happens to contain an unmapped type.
    """
    key = (sap_type or "").strip().upper()
    mapped = _SAP_TYPES.get(key)
    if mapped is None:
        logger.warning("Unmapped SAP field type %r; falling back to string.", sap_type)
        return dict(_STRING)
    # A DEC with no decimal places is an integer as far as JSON is concerned.
    if mapped is _BIG_NUMBER and decimals == 0:
        return dict(_INTEGER)
    return dict(mapped)


def json_schema_for_fields(fields: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Build a draft-07 object schema from ERPL field metadata.

    Accepts both shapes ERPL produces: ``sap_describe_fields`` rows mapped to
    dicts, and the ``fields`` STRUCT list returned by ``sap_odp_describe``.
    """
    properties: dict[str, Any] = {}
    for field in fields:
        name = field.get("technical_name") or field.get("field")
        if not name:
            continue
        prop = sap_type_to_json_schema(
            field.get("abap_type") or field.get("sap_type") or "",
            int(field.get("length") or 0),
            int(field.get("decimals") or 0),
        )
        text = field.get("text")
        if text:
            prop["description"] = text
        properties[name] = prop
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "additionalProperties": True,
        "properties": properties,
    }


def primary_key_for_fields(fields: Iterable[Mapping[str, Any]]) -> list[list[str]] | None:
    """Airbyte's nested primary-key shape, or None when SAP reports no key."""
    keys = [f.get("technical_name") or f.get("field") for f in fields if f.get("key") or f.get("is_key") in (True, "X")]
    keys = [k for k in keys if k]
    return [[k] for k in keys] or None


def coerce_value(value: Any) -> Any:
    """Return an orjson-serializable equivalent of a DuckDB value."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        # str() keeps full precision; float() would silently round money.
        return str(value)
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, datetime.time):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, (list, tuple)):
        return [coerce_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): coerce_value(v) for k, v in value.items()}
    if isinstance(value, datetime.timedelta):
        return str(value)
    return str(value)


def coerce_row(columns: Sequence[str], row: Sequence[Any]) -> dict[str, Any]:
    """Zip a DuckDB row into an orjson-safe record dict."""
    return {col: coerce_value(val) for col, val in zip(columns, row, strict=False)}
