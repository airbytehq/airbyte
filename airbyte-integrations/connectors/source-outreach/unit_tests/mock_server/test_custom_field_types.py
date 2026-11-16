# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from collections.abc import Iterator

import pytest
from jsonschema import validate

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import build_source

from .config import ConfigBuilder
from .request_builder import BASE_URL
from .utils import given_token, read_stream


_STREAM = "custom_field_types"
_REQUEST = HttpRequest(f"{BASE_URL}/types")

# Shapes copied from a live GET /api/v2/types response: one entry per object type, with the custom field
# settings under meta.validations. `definition` is a list for picklists, a currency code for currency fields
# and null for the other types.
_PROSPECT_VALIDATIONS = {
    "custom1": {"type": "string", "required": False, "label": "Lead Source Detail", "description": None, "definition": None},
    "custom2": {"type": "inclusion", "required": False, "label": "Region", "description": None, "definition": ["EMEA", "NA", "APAC"]},
}
_OPPORTUNITY_VALIDATIONS = {
    "custom2": {"type": "currency", "required": True, "label": "Expected ARR", "description": "Annual value", "definition": "USD"},
}


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker


def _types_response(entries: list[dict]) -> HttpResponse:
    return HttpResponse(json.dumps({"data": entries}), 200)


def _entry(object_type: str, validations: dict) -> dict:
    return {"type": object_type, "meta": {"validations": validations}}


def test_read_emits_one_record_per_object_type_with_meta_flattened(http_mocker: HttpMocker) -> None:
    given_token(http_mocker)
    http_mocker.get(
        _REQUEST,
        _types_response([_entry("Prospect", _PROSPECT_VALIDATIONS), _entry("Opportunity", _OPPORTUNITY_VALIDATIONS)]),
    )

    output = read_stream(_STREAM, SyncMode.full_refresh)

    assert not output.errors
    assert [message.record.data for message in output.records] == [
        {"type": "Prospect", "validations": _PROSPECT_VALIDATIONS},
        {"type": "Opportunity", "validations": _OPPORTUNITY_VALIDATIONS},
    ]
    http_mocker.assert_number_of_calls(_REQUEST, 1)


def test_read_emits_nothing_when_no_object_has_custom_fields(http_mocker: HttpMocker) -> None:
    given_token(http_mocker)
    http_mocker.get(_REQUEST, _types_response([]))

    output = read_stream(_STREAM, SyncMode.full_refresh)

    assert not output.errors
    assert output.records == []


def test_discovery_declares_full_refresh_with_type_primary_key() -> None:
    config = ConfigBuilder().build()
    discovery = discover(build_source(config), config)

    assert not discovery.errors
    stream = {s.name: s for s in discovery.catalog.catalog.streams}[_STREAM]
    assert [mode.value for mode in stream.supported_sync_modes] == ["full_refresh"]
    assert stream.source_defined_primary_key == [["type"]]


def test_discovered_schema_validates_read_records(http_mocker: HttpMocker) -> None:
    config = ConfigBuilder().build()
    discovery = discover(build_source(config), config)
    schema = {s.name: s for s in discovery.catalog.catalog.streams}[_STREAM].json_schema
    given_token(http_mocker)
    http_mocker.get(
        _REQUEST,
        _types_response([_entry("Prospect", _PROSPECT_VALIDATIONS), _entry("Opportunity", _OPPORTUNITY_VALIDATIONS)]),
    )

    output = read_stream(_STREAM, SyncMode.full_refresh, config=config)

    assert len(output.records) == 2
    for message in output.records:
        record = message.record.data
        assert record.keys() <= schema["properties"].keys()
        validate(record, schema)
