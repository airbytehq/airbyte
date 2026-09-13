"""DuckDB result-metadata helpers.

`DuckDBPyConnection.execute()` returns the *connection*, so there is no `.types`
attribute to read -- the column types live in ``description[i][1]``. Getting
that wrong silently drops streams from `discover`, so it lives in one place
with tests around it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

_STRING: dict[str, Any] = {"type": ["null", "string"]}

# fmt: off
_BY_PREFIX: tuple[tuple[tuple[str, ...], dict[str, Any]], ...] = (
    (("BOOLEAN",), {"type": ["null", "boolean"]}),
    (("TINYINT", "SMALLINT", "INTEGER", "BIGINT", "HUGEINT",
      "UTINYINT", "USMALLINT", "UINTEGER", "UBIGINT", "UHUGEINT"), {"type": ["null", "integer"]}),
    (("FLOAT", "DOUBLE", "DECIMAL", "REAL"), {"type": ["null", "number"]}),
    (("TIMESTAMP", "DATETIME"), {"type": ["null", "string"], "format": "date-time"}),
    (("DATE",), {"type": ["null", "string"], "format": "date"}),
    (("TIME",), {"type": ["null", "string"], "format": "time"}),
    (("BLOB", "BYTEA", "VARBINARY"), {"type": ["null", "string"], "contentEncoding": "base64"}),
    (("VARCHAR", "TEXT", "STRING", "UUID"), _STRING),
)
# fmt: on


def json_type_for(duckdb_type: Any) -> dict[str, Any]:
    """Map one DuckDB column type to a JSON Schema fragment."""
    name = str(duckdb_type).strip().upper()
    # Composite types share a prefix with their element type ("INTEGER[]"), so
    # they have to be caught before the prefix scan.
    if name.endswith("[]") or name.startswith(("STRUCT", "MAP", "UNION", "LIST")):
        return dict(_STRING)
    for prefixes, schema in _BY_PREFIX:
        if name.startswith(prefixes):
            return dict(schema)
    # Lists, structs, maps and anything else are emitted as their text form.
    return dict(_STRING)


def schema_from_description(description: Sequence[Sequence[Any]] | None) -> dict[str, Any]:
    """Build a draft-07 object schema from a DuckDB cursor description."""
    properties: dict[str, Any] = {}
    for column in description or []:
        properties[str(column[0])] = json_type_for(column[1])
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "additionalProperties": True,
        "properties": properties,
    }


def columns_of(description: Sequence[Sequence[Any]] | None) -> list[str]:
    return [str(column[0]) for column in description or []]


def has_column(schema: Mapping[str, Any], name: str) -> bool:
    return name in (schema.get("properties") or {})
