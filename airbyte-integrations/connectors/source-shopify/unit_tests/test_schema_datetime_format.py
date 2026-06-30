#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

import pytest

SCHEMAS_DIR = Path(__file__).parent.parent / "source_shopify" / "schemas"


def _collect_fields_at_path(schema_obj, path=""):
    """Walk a JSON schema and yield (dotted_path, field_def) for every leaf property."""
    if not isinstance(schema_obj, dict):
        return
    for key, definition in schema_obj.get("properties", {}).items():
        field_path = f"{path}.{key}" if path else key
        yield field_path, definition
        # Recurse into nested objects
        if "properties" in definition:
            yield from _collect_fields_at_path(definition, field_path)
        # Recurse into array items
        items = definition.get("items", {})
        if isinstance(items, dict) and "properties" in items:
            yield from _collect_fields_at_path(items, f"{field_path}[]")


@pytest.mark.parametrize(
    "schema_file, field_path",
    [
        pytest.param("orders.json", "processed_at", id="orders-processed_at"),
        pytest.param("orders.json", "customer.accepts_marketing_updated_at", id="orders-customer-accepts_marketing_updated_at"),
        pytest.param("orders.json", "refunds[].transactions[].created_at", id="orders-refunds-transactions-created_at"),
        pytest.param("orders.json", "refunds[].transactions[].processed_at", id="orders-refunds-transactions-processed_at"),
        pytest.param("order_refunds.json", "processed_at", id="order_refunds-processed_at"),
        pytest.param("order_refunds.json", "transactions[].created_at", id="order_refunds-transactions-created_at"),
        pytest.param("order_refunds.json", "transactions[].processed_at", id="order_refunds-transactions-processed_at"),
        pytest.param("draft_orders.json", "customer.accepts_marketing_updated_at", id="draft_orders-customer-accepts_marketing_updated_at"),
    ],
)
def test_datetime_fields_have_format_annotation(schema_file, field_path):
    schema = json.loads((SCHEMAS_DIR / schema_file).read_text())
    fields = dict(_collect_fields_at_path(schema))
    assert field_path in fields, f"Field {field_path} not found in {schema_file}"
    field_def = fields[field_path]
    assert field_def.get("format") == "date-time", (
        f"{schema_file}: {field_path} is missing '\"format\": \"date-time\"'. Got: {field_def}"
    )
