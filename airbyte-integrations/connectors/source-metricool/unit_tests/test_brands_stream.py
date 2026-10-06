# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the `brands` stream on `source-metricool`.

These cover the `url` and `title` properties added to the `brands` schema.
The `brands` schema declares `additionalProperties: true`, so raw records
already carried these two fields before they were declared. What the schema
addition actually changes is the *discovered catalog* -- the schema the
platform uses to create columns in the destination -- so that is what these
tests assert against, rather than the text of `manifest.yaml`.
"""

import logging
from pathlib import Path

import pytest
import requests_mock
from jsonschema import Draft7Validator

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"

_CONFIG = {
    "user_token": "test_user_token",
    "user_id": "1234567",
    "blog_ids": [7654321],
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-02-01T00:00:00Z",
}

_BRANDS_URL = "https://app.metricool.com/api/admin/simpleProfiles"


# Shape of a single `GET /admin/simpleProfiles` element (Metricool `PublicBlog`).
# NOTE: this is a hand-built fixture matching the published OpenAPI spec. If you
# have a real (sanitized) response body from the endpoint, replace it with that --
# only a real payload proves the fields are actually spelled `url` and `title`.
def _brand_record(brand_id: int = 7654321, **overrides):
    record = {
        "id": brand_id,
        "label": "Test Brand",
        "description": "A brand used in tests",
        "title": "Test Brand Site",
        "url": "https://example.com",
        "picture": "https://cdn.metricool.com/pic.png",
        "hash": "abc123",
        "deleted": False,
        "isShared": False,
        "userId": 1234567,
        "ownerUserId": 1234567,
        "ownerUsername": "owner@example.com",
        "role": "OWNER",
        "timezone": "Etc/UTC",
        "joinDate": 1700000000000,
        "firstConnectionDate": 1700000000000,
        "engagementRatio": 1.5,
        "facebook": "testbrand",
        "instagram": "testbrand",
        "youtube": "testbrand",
    }
    record.update(overrides)
    return record


def _get_source(config=None):
    config = config or _CONFIG
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config,
        state=StateBuilder().build(),
    )


def _brands_schema(config=None):
    """The `brands` json schema as the platform sees it, via discover."""
    catalog = _get_source(config).discover(logging.getLogger("airbyte"), config or _CONFIG)
    brands = next(stream for stream in catalog.streams if stream.name == "brands")
    return brands.json_schema


def _read_brands(body, config=None):
    config = config or _CONFIG
    source = _get_source(config)
    catalog = CatalogBuilder().with_stream("brands", SyncMode.full_refresh).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(_BRANDS_URL, json=body)
        return read(source, config, catalog)


# --------------------------------------------------------------------------
# 1. Discover exposes the new fields
# --------------------------------------------------------------------------


@pytest.mark.parametrize("field", ["url", "title"])
def test_discover_brands_schema_declares_new_field(field):
    """`url` and `title` are nullable strings in the discovered brands schema.

    This is the test that gates the user-visible fix: without it the fields
    never become columns in the destination.
    """
    properties = _brands_schema()["properties"]

    assert field in properties, f"`{field}` missing from the discovered brands schema"
    assert properties[field]["type"] == ["string", "null"]


# --------------------------------------------------------------------------
# 2. Real records validate against the declared types
# --------------------------------------------------------------------------


def test_brands_records_validate_against_declared_schema():
    """Every emitted record conforms to the schema the connector declares."""
    schema = _brands_schema()
    validator = Draft7Validator(schema)

    output = _read_brands([_brand_record(1), _brand_record(2, label="Second Brand")])

    assert len(output.records) == 2
    for message in output.records:
        validator.validate(message.record.data)


@pytest.mark.parametrize("field", ["url", "title"])
def test_brands_new_field_type_matches_payload(field):
    """The declared type for each new field accepts the value the API returns.

    Full-record validation cannot catch a wrong type here, because
    `additionalProperties: true` lets any undeclared shape through. Validating
    the value against its own subschema does.
    """
    schema = _brands_schema()
    output = _read_brands([_brand_record(1)])

    value = output.records[0].record.data[field]
    Draft7Validator(schema["properties"][field]).validate(value)


def test_brands_emits_new_field_values():
    """`url` and `title` reach the destination with their values intact."""
    output = _read_brands([_brand_record(1, title="Acme Blog", url="https://acme.example.com/blog")])

    data = output.records[0].record.data
    assert data["title"] == "Acme Blog"
    assert data["url"] == "https://acme.example.com/blog"


# --------------------------------------------------------------------------
# 3. Nulls and missing keys
# --------------------------------------------------------------------------


def test_brands_tolerates_null_and_missing_new_fields():
    """Brands without a site still sync: `url: null` and an absent `title`.

    Confirms `[string, "null"]` and leaving both out of `required` was correct.

    Note the CDK strips null-valued keys before emitting, so a brand that
    returns `"url": null` is indistinguishable from one that omits the key --
    neither reaches the destination as an explicit null.
    """
    schema = _brands_schema()
    validator = Draft7Validator(schema)

    with_null = _brand_record(1, url=None, title=None)
    without_keys = _brand_record(2)
    del without_keys["url"]
    del without_keys["title"]

    output = _read_brands([with_null, without_keys])

    assert output.errors == []
    assert len(output.records) == 2
    for message in output.records:
        validator.validate(message.record.data)
        assert "url" not in message.record.data
        assert "title" not in message.record.data


def test_brands_handles_empty_response():
    """No brands means no records and no failure."""
    output = _read_brands([])

    assert output.errors == []
    assert output.records == []


# --------------------------------------------------------------------------
# 4. No regression on what was already there
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "field,expected_type",
    [
        ("id", ["number", "null"]),
        ("userId", ["number", "null"]),
        ("ownerUserId", ["number", "null"]),
        ("joinDate", ["number", "null"]),
        ("firstConnectionDate", ["number", "null"]),
        ("engagementRatio", ["number", "null"]),
        ("deleted", ["boolean", "null"]),
        ("isShared", ["boolean", "null"]),
        ("description", ["string", "null"]),
        ("label", ["string", "null"]),
        ("hash", ["string", "null"]),
        ("picture", ["string", "null"]),
        ("role", ["string", "null"]),
        ("timezone", ["string", "null"]),
        ("ownerUsername", ["string", "null"]),
        ("facebook", ["string", "null"]),
        ("instagram", ["string", "null"]),
        ("youtube", ["string", "null"]),
    ],
)
def test_discover_brands_schema_preserves_existing_fields(field, expected_type):
    """Pre-existing brands properties keep their names and types.

    Guards against an indentation slip that nests the new properties under a
    sibling or drops one while hand-editing a 2000-line manifest.
    """
    properties = _brands_schema()["properties"]

    assert field in properties
    assert properties[field]["type"] == expected_type


def test_brands_stream_shape_unchanged():
    """The brands stream is still discoverable and still keyed on `id`."""
    catalog = _get_source().discover(logging.getLogger("airbyte"), _CONFIG)
    brands = next(stream for stream in catalog.streams if stream.name == "brands")

    assert brands.source_defined_primary_key == [["id"]]
    assert brands.supported_sync_modes == [SyncMode.full_refresh]
