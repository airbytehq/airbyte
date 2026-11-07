# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime
from typing import Any
from unittest import TestCase
from unittest.mock import patch

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_CONFIG = {
    "api_key": "test",
    "api_server": "us",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-02T00:00:00Z",
}
_ERROR_MESSAGE = (
    "Nylas returned 404 Not Found for the events of this calendar (the provider does not expose events for it, "
    "e.g. a subscribed, deleted or free/busy-only calendar); skipping it instead of failing the sync."
)
_EXPECTED_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "response_filters": [
        {
            "type": "HttpResponseFilter",
            "action": "IGNORE",
            "http_codes": [404],
            "error_message": _ERROR_MESSAGE,
        }
    ],
}


def _epoch(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


_START = _epoch(_CONFIG["start_date"])
_END = _epoch(_CONFIG["end_date"])
_GRANTS_REQUEST = HttpRequest(
    url="https://api.us.nylas.com/v3/grants",
    query_params={"limit": "50"},
)
_CALENDARS_REQUEST = HttpRequest(
    url="https://api.us.nylas.com/v3/grants/g1/calendars",
    query_params={"limit": "50"},
)


def _events_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        url="https://api.us.nylas.com/v3/grants/g1/events",
        query_params={
            "calendar_id": calendar_id,
            "end": str(_END),
            "limit": "50",
            "start": str(_START),
        },
    )


def _read_events(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("events", SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


@patch("time.sleep", lambda _: None)
class TestNylasErrorHandler(TestCase):
    def test_manifest_has_no_composite_error_handler(self) -> None:
        manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
        composite_error_handler_type = "".join(("Composite", "ErrorHandler"))

        def walk(value: Any) -> None:
            if isinstance(value, dict):
                assert value.get("type") != composite_error_handler_type
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(manifest)

        events_error_handler = manifest["definitions"]["streams"]["events"]["retriever"]["requester"]["error_handler"]
        assert events_error_handler == _EXPECTED_ERROR_HANDLER

    @HttpMocker()
    def test_events_404_is_skipped(self, http_mocker: HttpMocker) -> None:
        c1_events_request = _events_request("c1")
        c2_events_request = _events_request("c2")
        http_mocker.get(_GRANTS_REQUEST, HttpResponse(body=json.dumps({"data": [{"id": "g1"}]}), status_code=200))
        http_mocker.get(
            _CALENDARS_REQUEST,
            HttpResponse(body=json.dumps({"data": [{"id": "c1"}, {"id": "c2"}]}), status_code=200),
        )
        http_mocker.get(c1_events_request, HttpResponse(body="", status_code=404))
        http_mocker.get(
            c2_events_request,
            HttpResponse(
                body=json.dumps({"data": [{"id": "e1", "updated_at": _START + 3600}]}),
                status_code=200,
            ),
        )

        output = _read_events()

        assert output.errors == []
        assert len(output.records) == 1
        assert output.records[0].record.data == {"id": "e1", "updated_at": _START + 3600}
        http_mocker.assert_number_of_calls(c1_events_request, 1)
        http_mocker.assert_number_of_calls(c2_events_request, 1)

    @HttpMocker()
    def test_events_500_still_retries_and_fails(self, http_mocker: HttpMocker) -> None:
        events_request = _events_request("c1")
        http_mocker.get(_GRANTS_REQUEST, HttpResponse(body=json.dumps({"data": [{"id": "g1"}]}), status_code=200))
        http_mocker.get(_CALENDARS_REQUEST, HttpResponse(body=json.dumps({"data": [{"id": "c1"}]}), status_code=200))
        http_mocker.get(
            events_request,
            [HttpResponse(body="", status_code=500) for _ in range(6)],
        )

        output = _read_events(expecting_exception=True)

        assert output.errors
        http_mocker.assert_number_of_calls(events_request, 6)
