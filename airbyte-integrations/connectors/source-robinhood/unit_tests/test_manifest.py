# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import yaml
import pytest
from pathlib import Path


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    with open(MANIFEST_PATH, "r") as f:
        return yaml.safe_load(f)


EXPECTED_STREAMS = [
    "accounts",
    "positions",
    "portfolios",
    "orders",
    "instruments",
    "dividends",
    "watchlists",
    "options_positions",
    "options_orders",
]


def test_manifest_is_valid_yaml(manifest):
    assert manifest is not None
    assert manifest["type"] == "DeclarativeSource"


def test_manifest_version_present(manifest):
    assert "version" in manifest
    assert manifest["version"] is not None


def test_check_stream_configured(manifest):
    assert "check" in manifest
    assert manifest["check"]["type"] == "CheckStream"
    assert "accounts" in manifest["check"]["stream_names"]


@pytest.mark.parametrize("stream_name", EXPECTED_STREAMS, ids=EXPECTED_STREAMS)
def test_stream_defined(manifest, stream_name):
    stream_def = manifest["definitions"].get(f"{stream_name}_stream")
    assert stream_def is not None, f"Stream definition '{stream_name}_stream' not found"
    assert stream_def["type"] == "DeclarativeStream"
    assert stream_def["name"] == stream_name


@pytest.mark.parametrize("stream_name", EXPECTED_STREAMS, ids=EXPECTED_STREAMS)
def test_stream_has_schema(manifest, stream_name):
    stream_def = manifest["definitions"][f"{stream_name}_stream"]
    assert "schema_loader" in stream_def
    assert stream_def["schema_loader"]["type"] == "InlineSchemaLoader"
    schema_ref = stream_def["schema_loader"]["schema"]
    assert "$ref" in schema_ref
    ref_path = schema_ref["$ref"].replace("#/schemas/", "")
    assert ref_path in manifest["schemas"], f"Schema '{ref_path}' not found in schemas section"


@pytest.mark.parametrize("stream_name", EXPECTED_STREAMS, ids=EXPECTED_STREAMS)
def test_stream_has_primary_key(manifest, stream_name):
    stream_def = manifest["definitions"][f"{stream_name}_stream"]
    assert "primary_key" in stream_def, f"Stream '{stream_name}' should have a primary_key"
    assert len(stream_def["primary_key"]) > 0


@pytest.mark.parametrize("stream_name", EXPECTED_STREAMS, ids=EXPECTED_STREAMS)
def test_stream_uses_base_requester(manifest, stream_name):
    stream_def = manifest["definitions"][f"{stream_name}_stream"]
    requester = stream_def["retriever"]["requester"]
    assert "$ref" in requester
    assert requester["$ref"] == "#/definitions/base_requester"


@pytest.mark.parametrize("stream_name", EXPECTED_STREAMS, ids=EXPECTED_STREAMS)
def test_stream_has_paginator(manifest, stream_name):
    stream_def = manifest["definitions"][f"{stream_name}_stream"]
    retriever = stream_def["retriever"]
    assert "paginator" in retriever, f"Stream '{stream_name}' should have a paginator"


def test_streams_section_references_all_definitions(manifest):
    stream_refs = [s["$ref"] for s in manifest["streams"]]
    for stream_name in EXPECTED_STREAMS:
        expected_ref = f"#/definitions/{stream_name}_stream"
        assert expected_ref in stream_refs, f"Stream ref '{expected_ref}' not found in streams list"


def test_base_requester_config(manifest):
    base_req = manifest["definitions"]["base_requester"]
    assert base_req["type"] == "HttpRequester"
    assert base_req["url_base"] == "https://api.robinhood.com"
    assert base_req["http_method"] == "GET"


def test_authenticator_is_bearer(manifest):
    auth = manifest["definitions"]["authenticator"]
    assert auth["type"] == "BearerAuthenticator"
    assert auth["api_token"] == "{{ config['access_token'] }}"


def test_error_handler_retries(manifest):
    base_req = manifest["definitions"]["base_requester"]
    handler = base_req["error_handler"]
    assert handler["max_retries"] == 5
    retry_codes = handler["response_filters"][0]["http_codes"]
    assert 429 in retry_codes
    assert 500 in retry_codes
    assert 503 in retry_codes


def test_url_paginator_uses_cursor(manifest):
    paginator = manifest["definitions"]["url_paginator"]
    assert paginator["type"] == "DefaultPaginator"
    strategy = paginator["pagination_strategy"]
    assert strategy["type"] == "CursorPagination"
    assert "response.get('next'" in strategy["cursor_value"]
    assert "not response.get('next')" in strategy["stop_condition"]


def test_orders_stream_has_incremental_sync(manifest):
    orders = manifest["definitions"]["orders_stream"]
    assert "incremental_sync" in orders
    inc = orders["incremental_sync"]
    assert inc["type"] == "DatetimeBasedCursor"
    assert inc["cursor_field"] == "updated_at"


def test_spec_requires_access_token(manifest):
    spec = manifest["spec"]
    assert spec["type"] == "Spec"
    conn_spec = spec["connection_specification"]
    assert "access_token" in conn_spec["properties"]
    assert conn_spec["properties"]["access_token"]["airbyte_secret"] is True
    assert "access_token" in conn_spec["required"]


def test_spec_has_optional_start_date(manifest):
    conn_spec = manifest["spec"]["connection_specification"]
    assert "start_date" in conn_spec["properties"]
    assert "start_date" not in conn_spec["required"]


@pytest.mark.parametrize(
    "schema_name,required_field",
    [
        pytest.param("accounts", "account_number", id="accounts-pk"),
        pytest.param("positions", "url", id="positions-pk"),
        pytest.param("portfolios", "url", id="portfolios-pk"),
        pytest.param("orders", "id", id="orders-pk"),
        pytest.param("instruments", "id", id="instruments-pk"),
        pytest.param("dividends", "id", id="dividends-pk"),
        pytest.param("watchlists", "url", id="watchlists-pk"),
        pytest.param("options_positions", "url", id="options_positions-pk"),
        pytest.param("options_orders", "id", id="options_orders-pk"),
    ],
)
def test_schema_primary_key_is_non_nullable(manifest, schema_name, required_field):
    schema = manifest["schemas"][schema_name]
    pk_prop = schema["properties"][required_field]
    # Primary key fields should be non-nullable (type: string, not [string, "null"])
    assert pk_prop["type"] == "string", (
        f"Primary key '{required_field}' in '{schema_name}' should be non-nullable string"
    )


@pytest.mark.parametrize(
    "schema_name",
    EXPECTED_STREAMS,
    ids=EXPECTED_STREAMS,
)
def test_schema_allows_additional_properties(manifest, schema_name):
    schema = manifest["schemas"][schema_name]
    assert schema.get("additionalProperties") is True, (
        f"Schema '{schema_name}' should allow additional properties"
    )


@pytest.mark.parametrize(
    "stream_name,expected_path",
    [
        pytest.param("accounts", "/accounts/", id="accounts-path"),
        pytest.param("positions", "/positions/", id="positions-path"),
        pytest.param("portfolios", "/portfolios/", id="portfolios-path"),
        pytest.param("orders", "/orders/", id="orders-path"),
        pytest.param("instruments", "/instruments/", id="instruments-path"),
        pytest.param("dividends", "/dividends/", id="dividends-path"),
        pytest.param("watchlists", "/watchlists/", id="watchlists-path"),
        pytest.param("options_positions", "/options/positions/", id="options-positions-path"),
        pytest.param("options_orders", "/options/orders/", id="options-orders-path"),
    ],
)
def test_stream_endpoint_path(manifest, stream_name, expected_path):
    stream_def = manifest["definitions"][f"{stream_name}_stream"]
    requester = stream_def["retriever"]["requester"]
    assert requester["path"] == expected_path
