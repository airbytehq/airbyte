# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for source-criteo-marketing manifest.yaml.

Validates that the declarative manifest includes advertiserIds in the
statistics report request body and the connector spec.
"""

from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    with open(MANIFEST_PATH) as f:
        return yaml.safe_load(f)


def test_advertiser_ids_in_spec_properties(manifest):
    """The spec must expose advertiser_ids as a required string field."""
    properties = manifest["spec"]["connection_specification"]["properties"]
    assert "advertiser_ids" in properties, "spec must define advertiser_ids property"
    field = properties["advertiser_ids"]
    assert field["type"] == "string"


def test_advertiser_ids_is_required_in_spec(manifest):
    """advertiser_ids must be listed as a required field in the spec."""
    required = manifest["spec"]["connection_specification"]["required"]
    assert "advertiser_ids" in required, "advertiser_ids must be in the required list"


def test_ad_spend_daily_request_body_contains_advertiser_ids(manifest):
    """The ad_spend_daily stream request body must include advertiserIds
    referencing config['advertiser_ids']."""
    linked_body = manifest["definitions"]["linked"]["HttpRequester"]["request_body"]["value"]
    assert "advertiserIds" in linked_body, "request body must include advertiserIds key"
    value = linked_body["advertiserIds"]
    assert (
        "config['advertiser_ids']" in value or 'config["advertiser_ids"]' in value
    ), f"advertiserIds must reference config advertiser_ids, got: {value}"


@pytest.mark.parametrize(
    "field_name",
    [
        pytest.param("format", id="format"),
        pytest.param("advertiserIds", id="advertiserIds"),
        pytest.param("endDate", id="endDate"),
        pytest.param("metrics", id="metrics"),
        pytest.param("currency", id="currency"),
        pytest.param("startDate", id="startDate"),
        pytest.param("dimensions", id="dimensions"),
    ],
)
def test_ad_spend_daily_request_body_has_all_required_fields(manifest, field_name):
    """The statistics report request body must contain all required API fields."""
    linked_body = manifest["definitions"]["linked"]["HttpRequester"]["request_body"]["value"]
    assert field_name in linked_body, f"request body must include {field_name}"


def test_ad_spend_daily_is_check_stream(manifest):
    """ad_spend_daily must remain the check stream."""
    check_streams = manifest["check"]["stream_names"]
    assert "ad_spend_daily" in check_streams


def test_ad_spend_daily_stream_exists(manifest):
    """A stream named ad_spend_daily must exist in the manifest."""
    stream_names = [s["name"] for s in manifest["streams"]]
    assert "ad_spend_daily" in stream_names


def test_ad_spend_daily_uses_linked_request_body(manifest):
    """The ad_spend_daily stream requester must $ref the linked request body."""
    ad_spend = next(s for s in manifest["streams"] if s["name"] == "ad_spend_daily")
    request_body = ad_spend["retriever"]["requester"]["request_body"]
    assert "$ref" in request_body, "ad_spend_daily request_body must use $ref"
    assert request_body["$ref"] == "#/definitions/linked/HttpRequester/request_body"
