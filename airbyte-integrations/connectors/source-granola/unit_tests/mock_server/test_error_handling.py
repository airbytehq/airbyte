# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the shared HTTP error mapping.

`base_error_handler` maps `401`/`403` to config errors, `429` to rate limiting, and
`500`/`502`/`503`/`504` to a transient retry. `detailed_notes` and `note_transcripts` define their own
`response_filters`, which replace the shared list rather than merging with it, so each
stream is checked separately to catch a handler that drops the shared filters.
"""

import json
from typing import List
from unittest import TestCase
from unittest.mock import patch

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteErrorTraceMessage, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import GranolaRequestBuilder


_NOW = "2026-01-15T12:00:00Z"
_START_DATE = "2026-01-01"
_UPDATED_AFTER = "2026-01-01T00:00:00Z"
_NOTE_ID = "note-1"

_UNAUTHORIZED_MESSAGE = "Granola rejected the API key. It may be revoked or mistyped."
_FORBIDDEN_MESSAGE = "Granola denied access with this API key. The key may lack access to this workspace or note."
_RATE_LIMITED_MESSAGE = "Granola rate limit reached."
_SERVER_ERROR_MESSAGE = "Granola returned a server error."

# `max_retries: 5` on the error handler: the first attempt plus five retries.
_MAX_ATTEMPTS = 6

_STREAM_MODES = {
    "notes": SyncMode.incremental,
    "detailed_notes": SyncMode.full_refresh,
    "note_transcripts": SyncMode.full_refresh,
}


def _notes_request() -> HttpRequest:
    return GranolaRequestBuilder.notes_endpoint().with_updated_after(_UPDATED_AFTER).build()


def _notes_response() -> HttpResponse:
    body = {"notes": [{"id": _NOTE_ID, "title": "Meeting", "created_at": "2026-01-10T10:00:00Z"}], "hasMore": False}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _detailed_note_request() -> HttpRequest:
    return GranolaRequestBuilder.note_endpoint(_NOTE_ID).with_include("transcript").build()


def _detailed_note_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"id": _NOTE_ID, "title": "Meeting", "created_at": "2026-01-10T10:00:00Z"}), status_code=200)


def _transcript_request() -> HttpRequest:
    return GranolaRequestBuilder.transcript_endpoint(_NOTE_ID).build()


def _transcript_response() -> HttpResponse:
    body = {"transcript": [{"speaker": {"source": "microphone"}, "text": "hello"}], "hasMore": False}
    return HttpResponse(body=json.dumps(body), status_code=200)


# For each stream: the request under test, and the response that request returns on success.
_STREAM_REQUESTS = {
    "notes": (_notes_request, _notes_response),
    "detailed_notes": (_detailed_note_request, _detailed_note_response),
    "note_transcripts": (_transcript_request, _transcript_response),
}


def _error_response(status_code: int) -> HttpResponse:
    return HttpResponse(body=json.dumps({"code": f"HTTP_{status_code}"}), status_code=status_code)


def _mock_stream_request(http_mocker: HttpMocker, stream_name: str, responses: List[HttpResponse]) -> HttpRequest:
    """Mock the stream's own request with `responses`, and the parent `notes` request if the stream has one."""
    request_factory, _ = _STREAM_REQUESTS[stream_name]
    if stream_name != "notes":
        http_mocker.get(_notes_request(), _notes_response())
    request = request_factory()
    http_mocker.get(request, responses)
    return request


def _read(stream_name: str) -> EntrypointOutput:
    config = ConfigBuilder().with_start_date(_START_DATE).build()
    catalog = CatalogBuilder().with_stream(stream_name, _STREAM_MODES[stream_name]).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


def _errors(output: EntrypointOutput) -> List[AirbyteErrorTraceMessage]:
    return [message.trace.error for message in output.errors]


@freezegun.freeze_time(_NOW)
class TestRejectedApiKey(TestCase):
    """`401` and `403` fail every stream immediately as a config error, without retrying."""

    def test_401_fails_each_stream_as_a_config_error(self) -> None:
        for stream_name in _STREAM_REQUESTS:
            with self.subTest(stream=stream_name):
                self._assert_fails_as_config_error(stream_name, 401, _UNAUTHORIZED_MESSAGE)

    def test_403_fails_each_stream_as_a_config_error(self) -> None:
        for stream_name in _STREAM_REQUESTS:
            with self.subTest(stream=stream_name):
                self._assert_fails_as_config_error(stream_name, 403, _FORBIDDEN_MESSAGE)

    def _assert_fails_as_config_error(self, stream_name: str, status_code: int, expected_message: str) -> None:
        with HttpMocker() as http_mocker:
            request = _mock_stream_request(http_mocker, stream_name, [_error_response(status_code)])

            output = _read(stream_name)

            assert output.records == []
            first_error = _errors(output)[0]
            assert first_error.failure_type == FailureType.config_error
            assert first_error.message == expected_message
            http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time(_NOW)
@patch("time.sleep", lambda _: None)
class TestRateLimited(TestCase):
    def test_429_is_retried_until_it_succeeds(self) -> None:
        for stream_name in _STREAM_REQUESTS:
            with self.subTest(stream=stream_name), HttpMocker() as http_mocker:
                _, success_response = _STREAM_REQUESTS[stream_name]
                rate_limited = HttpResponse(body="{}", status_code=429, headers={"Retry-After": "1"})
                request = _mock_stream_request(http_mocker, stream_name, [rate_limited, success_response()])

                output = _read(stream_name)

                assert output.errors == []
                assert len(output.records) == 1
                http_mocker.assert_number_of_calls(request, 2)

    @HttpMocker()
    def test_429_fails_as_transient_once_retries_are_exhausted(self, http_mocker: HttpMocker) -> None:
        request = _mock_stream_request(http_mocker, "notes", [_error_response(429)] * _MAX_ATTEMPTS)

        output = _read("notes")

        assert output.records == []
        errors = _errors(output)
        assert errors[0].failure_type == FailureType.transient_error
        assert any(_RATE_LIMITED_MESSAGE in (error.message or "") for error in errors)
        assert not any("retrying" in (error.message or "") for error in errors)
        http_mocker.assert_number_of_calls(request, _MAX_ATTEMPTS)


@freezegun.freeze_time(_NOW)
@patch("time.sleep", lambda _: None)
class TestServerError(TestCase):
    def test_5xx_is_retried_until_it_succeeds(self) -> None:
        for stream_name in _STREAM_REQUESTS:
            with self.subTest(stream=stream_name), HttpMocker() as http_mocker:
                _, success_response = _STREAM_REQUESTS[stream_name]
                responses = [_error_response(500), _error_response(503), success_response()]
                request = _mock_stream_request(http_mocker, stream_name, responses)

                output = _read(stream_name)

                assert output.errors == []
                assert len(output.records) == 1
                http_mocker.assert_number_of_calls(request, 3)

    def test_5xx_fails_as_transient_once_retries_are_exhausted(self) -> None:
        for status_code in (500, 502, 503, 504):
            with self.subTest(status_code=status_code), HttpMocker() as http_mocker:
                request = _mock_stream_request(http_mocker, "notes", [_error_response(status_code)] * _MAX_ATTEMPTS)

                output = _read("notes")

                assert output.records == []
                first_error = _errors(output)[0]
                assert first_error.failure_type == FailureType.transient_error
                assert first_error.message.endswith(f"Exception: {_SERVER_ERROR_MESSAGE}")
                http_mocker.assert_number_of_calls(request, _MAX_ATTEMPTS)

    def test_5xx_on_child_streams_fails_as_transient(self) -> None:
        for stream_name in ("detailed_notes", "note_transcripts"):
            with self.subTest(stream=stream_name), HttpMocker() as http_mocker:
                request = _mock_stream_request(http_mocker, stream_name, [_error_response(503)] * _MAX_ATTEMPTS)

                output = _read(stream_name)

                first_error = _errors(output)[0]
                assert first_error.failure_type == FailureType.transient_error
                http_mocker.assert_number_of_calls(request, _MAX_ATTEMPTS)
