# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the `speeches` stream error handler."""

import json
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

import yaml
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_STREAM_NAME = "speeches"
_BASE_URL = "https://tavusapi.com"
_CONFIG = {"api_key": "test-key", "start_date": "2024-01-01T00:00:00Z"}
_SPEECH_REQUEST = HttpRequest(
    url=f"{_BASE_URL}/v2/speech",
    query_params={"page": "1", "limit": "50"},
)


def _speech(speech_id: str) -> Dict[str, Any]:
    return {
        "speech_id": speech_id,
        "updated_at": "2024-06-01T00:00:00.000000Z",
    }


def _speeches_response(*speeches: Dict[str, Any]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"data": list(speeches)}), status_code=200)


def _read(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


@patch("time.sleep", lambda _: None)
class TestTavusErrorHandler(TestCase):
    @HttpMocker()
    def test_speeches_records_are_emitted(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_SPEECH_REQUEST, _speeches_response(_speech("speech-1"), _speech("speech-2")))

        output = _read()

        assert [record.record.data["speech_id"] for record in output.records] == ["speech-1", "speech-2"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_SPEECH_REQUEST, 1)

    @HttpMocker()
    def test_500_is_ignored_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _SPEECH_REQUEST,
            HttpResponse(body=json.dumps({"message": "Need subscription plan"}), status_code=500),
        )

        output = _read()

        assert output.records == []
        assert output.errors == []
        http_mocker.assert_number_of_calls(_SPEECH_REQUEST, 1)

    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _SPEECH_REQUEST,
            [
                HttpResponse(body="", status_code=429),
                _speeches_response(_speech("speech-1")),
            ],
        )

        output = _read()

        assert [record.record.data["speech_id"] for record in output.records] == ["speech-1"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_SPEECH_REQUEST, 2)

    @HttpMocker()
    def test_403_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_SPEECH_REQUEST, HttpResponse(body="", status_code=403))

        output = _read(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_SPEECH_REQUEST, 1)

    def test_manifest_uses_default_error_handler_with_500_ignore_filter(self) -> None:
        manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
        requester = manifest["definitions"]["streams"]["speeches"]["retriever"]["requester"]

        assert requester["error_handler"]["type"] == "DefaultErrorHandler"
        assert requester["error_handler"]["response_filters"] == [
            {
                "type": "HttpResponseFilter",
                "action": "IGNORE",
                "http_codes": [500],
                "error_message": "Need subscription plan",
            }
        ]
