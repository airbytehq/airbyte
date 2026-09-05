#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Dict, List

import pytest
from unit_tests.conftest import get_source

from integration.config import ConfigBuilder


# `name` is a legitimate Stripe property name (customers, coupons, plans, ...), so it is only forbidden
# as a key of a schema node itself. `$parameters` is never legitimate anywhere in a record schema.
_FORBIDDEN_SCHEMA_KEYS = ("$parameters", "name")
_SUBSCHEMA_KEYWORDS = ("items", "additionalProperties", "not")
_SUBSCHEMA_LIST_KEYWORDS = ("anyOf", "oneOf", "allOf")


def _find_leaked_parameters(schema: Any, path: str = "") -> List[str]:
    """Walk a JSON schema and return the paths where dynamic stream `$parameters`/`name` leaked in."""
    if not isinstance(schema, dict):
        return []

    leaks = [f"{path or '<root>'}[{key}]" for key in _FORBIDDEN_SCHEMA_KEYS if key in schema]

    properties = schema.get("properties")
    if isinstance(properties, dict):
        for property_name, property_schema in properties.items():
            if property_name == "$parameters":
                leaks.append(f"{path}.properties.$parameters")
            leaks += _find_leaked_parameters(property_schema, f"{path}.properties.{property_name}")

    for keyword in _SUBSCHEMA_KEYWORDS:
        leaks += _find_leaked_parameters(schema.get(keyword), f"{path}.{keyword}")

    for keyword in _SUBSCHEMA_LIST_KEYWORDS:
        subschemas = schema.get(keyword)
        if isinstance(subschemas, list):
            for index, subschema in enumerate(subschemas):
                leaks += _find_leaked_parameters(subschema, f"{path}.{keyword}[{index}]")

    return leaks


@pytest.mark.parametrize("event_based_incremental_sync_mode", ["events", "hydrated_events"])
def test_given_any_incremental_sync_mode_when_discover_then_schemas_have_no_dynamic_stream_parameters(
    event_based_incremental_sync_mode: str,
) -> None:
    config = ConfigBuilder().with_event_based_incremental_sync_mode(event_based_incremental_sync_mode).build()
    catalog = get_source(config).discover(logging.getLogger(), config)

    assert catalog.streams, "Expected the source to discover at least one stream"

    leaks: Dict[str, List[str]] = {}
    for stream in catalog.streams:
        stream_leaks = _find_leaked_parameters(stream.json_schema)
        if stream_leaks:
            leaks[stream.name] = stream_leaks

    assert not leaks, f"Dynamic stream parameters leaked into discovered schemas: {leaks}"
