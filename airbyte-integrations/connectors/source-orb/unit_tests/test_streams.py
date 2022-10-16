#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_orb.source import CreditsLedgerEntries, OrbStream


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(OrbStream, "path", "v0/example_endpoint")
    mocker.patch.object(OrbStream, "primary_key", "id")
    mocker.patch.object(OrbStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = OrbStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"limit": OrbStream.page_size}
    assert stream.request_params(**inputs) == expected_params


@pytest.mark.parametrize(
    ("mock_response", "expected_token"),
    [
        ({}, None),
        (dict(pagination_metadata=dict(has_more=True, next_cursor="orb-test-cursor")), dict(cursor="orb-test-cursor")),
        (dict(pagination_metadata=dict(has_more=False)), None),
    ],
)
def test_next_page_token(patch_base_class, mocker, mock_response, expected_token):
    stream = OrbStream()
    response = mocker.MagicMock()
    response.json.return_value = mock_response
    inputs = {"response": response}
    assert stream.next_page_token(**inputs) == expected_token


@pytest.mark.parametrize(
    ("mock_response", "expected_parsed_objects"),
    [
        ({}, []),
        (dict(data=[]), []),
        (dict(data=[{"id": "test-customer-id"}]), [{"id": "test-customer-id"}]),
        (dict(data=[{"id": "test-customer-id"}, {"id": "test-customer-id-2"}]), [{"id": "test-customer-id"}, {"id": "test-customer-id-2"}]),
    ],
)
def test_parse_response(patch_base_class, mocker, mock_response, expected_parsed_objects):
    stream = OrbStream()
    response = mocker.MagicMock()
    response.json.return_value = mock_response
    inputs = {"response": response}
    assert list(stream.parse_response(**inputs)) == expected_parsed_objects


def test_http_method(patch_base_class):
    stream = OrbStream()
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize("event_properties_keys", [["foo-property"], ["foo-property", "bar-property"], None])
def test_credit_ledger_entries_schema(patch_base_class, mocker, event_properties_keys):
    stream = CreditsLedgerEntries(string_event_properties_keys=event_properties_keys)
    json_schema = stream.get_json_schema()

    assert "event" in json_schema["properties"]
    if event_properties_keys is None:
        assert json_schema["properties"]["event"]["properties"]["properties"]["properties"] == {}
    else:
        for property_key in event_properties_keys:
            assert property_key in json_schema["properties"]["event"]["properties"]["properties"]["properties"]
