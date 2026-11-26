# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from collections.abc import Mapping
from typing import Any

import pytest
from conftest import get_source
from mock_server.config import ConfigBuilder


# `list_membership.isDeleted` is newly requested. The connector already requested the other six without declaring them.
ADDED_FIELDS = [
    ("list_membership", "isDeleted", "boolean"),
    ("lists", "campaignId", "integer"),
    ("emails", "folderId", "integer"),
    ("emails", "listId", "integer"),
    ("emails", "trackerDomainId", "integer"),
    ("forms", "trackerDomainId", "integer"),
    ("custom_redirects", "trackerDomain", "object"),
]


@pytest.fixture(scope="module")
def schemas() -> dict[str, Mapping[str, Any]]:
    config = ConfigBuilder().build()
    catalog = get_source(config).discover(logging.getLogger("airbyte"), config)
    return {stream.name: stream.json_schema for stream in catalog.streams}


@pytest.mark.parametrize(("stream", "field", "kind"), ADDED_FIELDS, ids=[f"{stream}.{field}" for stream, field, _ in ADDED_FIELDS])
def test_added_field_is_declared_with_its_type(schemas: dict[str, Mapping[str, Any]], stream: str, field: str, kind: str) -> None:
    assert set(schemas[stream]["properties"][field]["type"]) == {"null", kind}


def test_custom_redirects_declares_the_domain_inside_tracker_domain(schemas: dict[str, Mapping[str, Any]]) -> None:
    tracker_domain = schemas["custom_redirects"]["properties"]["trackerDomain"]

    assert set(tracker_domain["properties"]["domain"]["type"]) == {"null", "string"}


def test_custom_redirects_keeps_the_flat_tracker_domain_key(schemas: dict[str, Mapping[str, Any]]) -> None:
    # No record carries this key. It stays because removing a declared field is a breaking change.
    assert "trackerDomain.domain" in schemas["custom_redirects"]["properties"]
