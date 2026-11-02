# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase
from unittest.mock import patch

import yaml
from freezegun import freeze_time
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAMES = [
    "message_events",
    "sending_domains",
    "ab_test",
    "templates",
    "recipients",
    "subaccounts",
    "snippets",
]
_TEMPLATES_URL = "https://api.sparkpost.com/api/v1/templates"
_EVENTS_URL = "https://api.sparkpost.com/api/v1/events/message"
_CONFIG = {"api_key": "test-key", "start_date": "2026-01-01T00:00:00Z", "api_prefix": "api"}
_TEMPLATES_REQUEST = HttpRequest(_TEMPLATES_URL)
_FIRST_EVENTS_REQUEST = HttpRequest(
    _EVENTS_URL,
    query_params={
        "per_page": "1000",
        "from": "2026-01-05T00:00:00Z",
        "to": "2026-01-14T23:59:00Z",
    },
)
_SECOND_EVENTS_REQUEST = HttpRequest(
    _EVENTS_URL,
    query_params={
        "per_page": "1000",
        "from": "2026-01-05T00:00:00Z",
        "to": "2026-01-14T23:59:00Z",
        "cursor": "abc123",
    },
)
_DEFAULT_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "backoff_strategies": [{"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 5}],
}
_MAX_RETRIES = 5


def _templates_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"results": [{"id": "t1"}]}), status_code=200)


def _events_response(event_id: str, next_link: str | None = None) -> HttpResponse:
    body = {
        "results": [{"event_id": event_id, "timestamp": "2026-01-06T00:00:00.000Z"}],
    }
    if next_link:
        body["links"] = {"next": next_link}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read_stream(stream_name: str, sync_mode: SyncMode, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog, expecting_exception=expecting_exception)


def _read_templates(expecting_exception: bool = False) -> EntrypointOutput:
    return _read_stream("templates", SyncMode.full_refresh, expecting_exception=expecting_exception)


def _read_message_events(expecting_exception: bool = False) -> EntrypointOutput:
    return _read_stream("message_events", SyncMode.incremental, expecting_exception=expecting_exception)


def test_every_stream_uses_a_single_default_error_handler() -> None:
    manifest_text = _YAML_FILE_PATH.read_text()
    manifest = yaml.safe_load(manifest_text)

    for stream_name in _STREAM_NAMES:
        requester = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]
        assert requester["error_handler"] == _DEFAULT_ERROR_HANDLER

    assert "Composite" + "ErrorHandler" not in manifest_text


@patch("time.sleep", lambda _: None)
class TestSparkPostErrorHandler(TestCase):
    @HttpMocker()
    def test_5xx_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _TEMPLATES_REQUEST,
            [
                HttpResponse(body="", status_code=500),
                HttpResponse(body="", status_code=503),
                _templates_response(),
            ],
        )

        output = _read_templates()

        assert [record.record.data["id"] for record in output.records] == ["t1"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_TEMPLATES_REQUEST, 3)

    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_TEMPLATES_REQUEST, [HttpResponse(body="", status_code=429), _templates_response()])

        output = _read_templates()

        assert [record.record.data["id"] for record in output.records] == ["t1"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_TEMPLATES_REQUEST, 2)

    @HttpMocker()
    def test_persistent_5xx_stops_after_max_retries(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_TEMPLATES_REQUEST, HttpResponse(body="", status_code=500))

        output = _read_templates(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_TEMPLATES_REQUEST, _MAX_RETRIES + 1)

    @HttpMocker()
    def test_403_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_TEMPLATES_REQUEST, HttpResponse(body="", status_code=403))

        output = _read_templates(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_TEMPLATES_REQUEST, 1)

    @freeze_time("2026-01-15T00:00:00Z")
    @HttpMocker()
    def test_message_events_paginates_with_exact_incremental_query_params(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_FIRST_EVENTS_REQUEST, _events_response("e1", "/api/v1/events/message?cursor=abc123&per_page=1000"))
        http_mocker.get(_SECOND_EVENTS_REQUEST, _events_response("e2"))

        output = _read_message_events()

        assert [record.record.data["event_id"] for record in output.records] == ["e1", "e2"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_FIRST_EVENTS_REQUEST, 1)
        http_mocker.assert_number_of_calls(_SECOND_EVENTS_REQUEST, 1)

    @freeze_time("2026-01-15T00:00:00Z")
    @HttpMocker()
    def test_message_events_retries_first_page_then_paginates(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _FIRST_EVENTS_REQUEST,
            [
                HttpResponse(body="", status_code=500),
                _events_response("e1", "/api/v1/events/message?cursor=abc123&per_page=1000"),
            ],
        )
        http_mocker.get(_SECOND_EVENTS_REQUEST, _events_response("e2"))

        output = _read_message_events()

        assert [record.record.data["event_id"] for record in output.records] == ["e1", "e2"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_FIRST_EVENTS_REQUEST, 2)
        http_mocker.assert_number_of_calls(_SECOND_EVENTS_REQUEST, 1)
