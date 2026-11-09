# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for RentCast stream error handlers."""

import json
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

import pytest
import yaml
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.rentcast.io/v1/"
_ADDRESS = "123 Main St, Austin, TX 78704"
_ERROR_MESSAGE_CONTAINS = "The required query parameters 'address' or 'latitude'/'longitude' were not provided"
_ERROR_BODY = {"message": _ERROR_MESSAGE_CONTAINS}
_CONFIG = {
    "api_key": "test-key",
    "zipcode": "78704",
    "address": _ADDRESS,
}
_STREAMS = {
    "Rental Listings": {
        "path": "listings/rental/long-term",
        "query_params": {"address": _ADDRESS, "zipCode": "78704"},
        "error_message": "Please provide a zipcode",
    },
    "Statistics": {
        "path": "markets",
        "query_params": {"zipCode": "78704"},
        "error_message": "Please provide a zipcode",
    },
    "Value Estimate": {
        "path": "avm/value",
        "query_params": {"address": _ADDRESS},
        "error_message": "Please provide either an address or a latitude and longitude.",
    },
    "Rent Estimate": {
        "path": "avm/rent/long-term",
        "query_params": {"address": _ADDRESS},
        "error_message": "Please provide either an address or a latitude and longitude.",
    },
}


def _request(stream_name: str) -> HttpRequest:
    stream = _STREAMS[stream_name]
    return HttpRequest(url=f"{_BASE_URL}{stream['path']}", query_params=stream["query_params"])


_REQUESTS = {stream_name: _request(stream_name) for stream_name in _STREAMS}


def _response(*records: Dict[str, Any]) -> HttpResponse:
    return HttpResponse(body=json.dumps(list(records)), status_code=200)


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


@patch("time.sleep", lambda _: None)
class TestRentcastErrorHandler(TestCase):
    @HttpMocker()
    def test_records_are_emitted(self, http_mocker: HttpMocker) -> None:
        for stream_name in _STREAMS:
            http_mocker.get(_REQUESTS[stream_name], _response({"id": "record-1"}, {"id": "record-2"}))

        for stream_name in _STREAMS:
            output = _read(stream_name)

            assert [record.record.data["id"] for record in output.records] == ["record-1", "record-2"]
            assert output.errors == []
            http_mocker.assert_number_of_calls(_REQUESTS[stream_name], 1)

    @HttpMocker()
    def test_400_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        for stream_name in _STREAMS:
            http_mocker.get(
                _REQUESTS[stream_name],
                HttpResponse(body=json.dumps(_ERROR_BODY), status_code=400),
            )

        for stream_name in _STREAMS:
            output = _read(stream_name, expecting_exception=True)

            assert output.records == []
            assert output.errors
            assert _STREAMS[stream_name]["error_message"] in output.errors[0].trace.error.message
            http_mocker.assert_number_of_calls(_REQUESTS[stream_name], 1)

    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        for stream_name in _STREAMS:
            http_mocker.get(
                _REQUESTS[stream_name],
                [
                    HttpResponse(body="", status_code=429),
                    _response({"id": "record-1"}),
                ],
            )

        for stream_name in _STREAMS:
            output = _read(stream_name)

            assert [record.record.data["id"] for record in output.records] == ["record-1"]
            assert output.errors == []
            http_mocker.assert_number_of_calls(_REQUESTS[stream_name], 2)


@pytest.mark.parametrize("stream_name", list(_STREAMS))
def test_manifest_uses_default_error_handler_with_expected_filter(stream_name: str) -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    requester = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]

    assert requester["error_handler"]["type"] == "DefaultErrorHandler"
    assert requester["error_handler"]["response_filters"] == [
        {
            "type": "HttpResponseFilter",
            "action": "FAIL",
            "error_message_contains": _ERROR_MESSAGE_CONTAINS,
            "http_codes": [400],
            "error_message": _STREAMS[stream_name]["error_message"],
        }
    ]
