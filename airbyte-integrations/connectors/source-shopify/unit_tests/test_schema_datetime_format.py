#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

import pytest


SCHEMAS_DIR = Path(__file__).parent.parent / "source_shopify" / "schemas"

DATETIME_SUFFIXES = ("_at", "_on", "_date")

# Fields whose name matches the datetime heuristic but which are not timestamps.
EXEMPT = {
    # `compare_at` is a price, not a timestamp.
    "abandoned_checkouts.json::tax_lines[].compare_at",
    "abandoned_checkouts.json::shipping_lines[].tax_lines[].compare_at",
    # Nested inside the `customer` object, which typed destinations store as a single JSON column,
    # so annotating it would change no destination column type. The top-level copy on `customers`
    # is annotated.
    "orders.json::customer.accepts_marketing_updated_at",
    "draft_orders.json::customer.accepts_marketing_updated_at",
}


def _branches(definition):
    """Yield a property definition and every anyOf/oneOf branch nested under it."""
    yield definition
    for keyword in ("anyOf", "oneOf"):
        for branch in definition.get(keyword, []):
            if isinstance(branch, dict):
                yield from _branches(branch)


def _walk(schema_obj, path=""):
    """Yield (dotted_path, definition) for every property, descending through objects, arrays and anyOf/oneOf."""
    if not isinstance(schema_obj, dict):
        return
    for key, definition in schema_obj.get("properties", {}).items():
        if not isinstance(definition, dict):
            continue
        field_path = f"{path}.{key}" if path else key
        yield field_path, definition
        for branch in _branches(definition):
            yield from _walk(branch, field_path)
            items = branch.get("items")
            if isinstance(items, dict):
                for item_branch in _branches(items):
                    yield from _walk(item_branch, f"{field_path}[]")


def _is_string(definition):
    for branch in _branches(definition):
        declared = branch.get("type")
        if declared == "string" or (isinstance(declared, list) and "string" in declared):
            return True
    return False


@pytest.mark.parametrize("schema_file", sorted(p.name for p in SCHEMAS_DIR.glob("*.json")))
def test_datetime_fields_have_format_annotation(schema_file):
    """Every string field whose name looks like a timestamp must declare `format: date-time`."""
    schema = json.loads((SCHEMAS_DIR / schema_file).read_text())
    missing = []
    for field_path, definition in _walk(schema):
        name = field_path.rsplit(".", 1)[-1].removesuffix("[]")
        if not name.endswith(DATETIME_SUFFIXES) or not _is_string(definition):
            continue
        if f"{schema_file}::{field_path}" in EXEMPT:
            continue
        if not any(branch.get("format") == "date-time" for branch in _branches(definition)):
            missing.append(field_path)
    assert not missing, f'{schema_file}: datetime fields missing \'"format": "date-time"\': {sorted(set(missing))}'
