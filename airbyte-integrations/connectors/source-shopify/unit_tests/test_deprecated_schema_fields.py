#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""Tests guarding against regressions that would re-introduce Shopify-deprecated fields.

Shopify removed ``pre_tax_price`` and ``pre_tax_price_set`` from order line items in the
REST Admin API (https://shopify.dev/changelog/removal-of-pretaxprice-from-the-order-rest-admin-api).
These fields were only ever populated for stores with the Avalara AvaTax 1.0 integration,
which Shopify deprecated in April 2025. The fields must not be redeclared in the connector
schemas, otherwise the connector would advertise properties that the upstream API no longer
returns.
"""

import json
from pathlib import Path
from typing import Iterator

import pytest


SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "source_shopify" / "schemas"
DEPRECATED_FIELDS = ("pre_tax_price", "pre_tax_price_set")


def _walk_properties(node: object) -> Iterator[str]:
    """Yield every property name declared anywhere within a JSON Schema node."""
    if isinstance(node, dict):
        properties = node.get("properties")
        if isinstance(properties, dict):
            for name, child in properties.items():
                yield name
                yield from _walk_properties(child)
        for key, value in node.items():
            if key == "properties":
                continue
            yield from _walk_properties(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_properties(item)


@pytest.mark.parametrize("schema_name", ["orders.json", "order_refunds.json"])
def test_deprecated_pre_tax_price_fields_removed(schema_name: str) -> None:
    schema_path = SCHEMAS_DIR / schema_name
    schema = json.loads(schema_path.read_text())
    declared = set(_walk_properties(schema))
    for field in DEPRECATED_FIELDS:
        assert field not in declared, (
            f"{schema_name} still declares deprecated field '{field}' which Shopify removed "
            "from the REST Admin API on 2026-03-23."
        )
