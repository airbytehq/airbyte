# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from collections.abc import Mapping
from typing import Any

import pytest

from unit_tests.conftest import CONFIG, get_source


ADDED_FIELDS = [
    ("dashboards", "is_read_only", "boolean", None, None),
    ("monitors", "creator.id", "integer", None, None),
    ("monitors", "draft_status", "string", None, None),
    ("monitors", "matching_downtimes[].active", "boolean", None, None),
    ("monitors", "matching_downtimes[].groups", "array", None, None),
    ("monitors", "matching_downtimes[].monitor_id", "integer", None, None),
    ("service_level_objectives", "sli_specification", "object", None, None),
    ("users", "attributes.allowed_login_methods", "array", None, "string"),
    ("users", "attributes.is_access_configurable_bot", "boolean", None, None),
    ("users", "attributes.last_login_time", "string", "date-time", None),
    ("users", "attributes.mfa_enabled", "boolean", None, None),
    ("users", "attributes.uuid", "string", None, None),
]


@pytest.fixture(scope="module")
def schemas() -> dict[str, Mapping[str, Any]]:
    catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)
    return {stream.name: stream.json_schema for stream in catalog.streams}


def _declared(schema: Mapping[str, Any], path: str) -> Mapping[str, Any]:
    for part in path.split("."):
        schema = schema["properties"][part.removesuffix("[]")]
        if part.endswith("[]"):
            schema = schema["items"]
    return schema


def _kinds(schema: Mapping[str, Any]) -> set[str]:
    kinds = schema["type"]
    return set(kinds) if isinstance(kinds, list) else {kinds}


@pytest.mark.parametrize(
    ("stream", "path", "kind", "date_format", "item_kind"),
    ADDED_FIELDS,
    ids=[f"{stream}.{path}" for stream, path, *_ in ADDED_FIELDS],
)
def test_added_field_is_declared_with_its_type(
    schemas: dict[str, Mapping[str, Any]],
    stream: str,
    path: str,
    kind: str,
    date_format: str | None,
    item_kind: str | None,
) -> None:
    declared = _declared(schemas[stream], path)

    assert _kinds(declared) == {kind, "null"}
    assert declared.get("format") == date_format
    assert ("items" in declared) == bool(item_kind)
    if item_kind:
        assert _kinds(declared["items"]) - {"null"} == {item_kind}
