# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock server tests for sync-token incremental sync on `candidates`."""

import json
import logging
from typing import Any, Dict, List, Optional
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import AshbyRequestBuilder


_STREAM_NAME = "candidates"
_COMMITTED_AT = "2026-10-01T00:00:00Z"


def _page(
    records: List[Dict[str, Any]],
    *,
    more_data_available: bool,
    next_cursor: Optional[str] = None,
    sync_token: Optional[str] = None,
) -> HttpResponse:
    body: Dict[str, Any] = {
        "success": True,
        "results": records,
        "moreDataAvailable": more_data_available,
    }
    if next_cursor is not None:
        body["nextCursor"] = next_cursor
    if sync_token is not None:
        body["syncToken"] = sync_token
    return HttpResponse(body=json.dumps(body), status_code=200)


def _error(code: str, message: str) -> HttpResponse:
    return HttpResponse(
        body=json.dumps({"success": False, "errorInfo": {"code": code, "message": message}}),
        status_code=200,
    )


def _candidates_request(cursor: Optional[str] = None, sync_token: Optional[str] = None) -> HttpRequest:
    builder = AshbyRequestBuilder.endpoint("/candidate.list").with_api_key("test-api-key").with_limit(100)
    if cursor is not None:
        builder = builder.with_cursor(cursor)
    if sync_token is not None:
        builder = builder.with_body_field("syncToken", sync_token)
    return builder.build()


def _cursor_state(token: str):
    return (
        StateBuilder()
        .with_stream_state(
            _STREAM_NAME,
            {"state_type": "sync_token", "token": token, "committed_at": _COMMITTED_AT},
        )
        .build()
    )


def _read(state=None) -> EntrypointOutput:
    config = ConfigBuilder().build()
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)


def _emitted_tokens(output: EntrypointOutput) -> List[Any]:
    return [
        message.state.stream.stream_state.__dict__.get("token")
        for message in output.state_messages
        if message.state and message.state.stream and message.state.stream.stream_state
    ]


class TestCandidates(TestCase):
    def test_bootstrap_pages_without_a_token_then_commits_the_terminal_token(self):
        first_page = _candidates_request()
        second_page = _candidates_request(cursor="c1")
        with HttpMocker() as http_mocker:
            http_mocker.post(
                first_page,
                _page(
                    [{"id": "candidate-1"}, {"id": "candidate-2"}],
                    more_data_available=True,
                    next_cursor="c1",
                ),
            )
            http_mocker.post(
                second_page,
                _page([{"id": "candidate-3"}], more_data_available=False, sync_token="tok1"),
            )

            output = _read()

        assert output.errors == []
        assert len(output.records) == 3
        stream_state = output.most_recent_state.stream_state.__dict__
        assert stream_state["state_type"] == "sync_token"
        assert stream_state["token"] == "tok1"
        assert "committed_at" in stream_state
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    def test_incremental_sync_replays_the_token_on_each_page_and_commits_the_terminal_token(self):
        first_page = _candidates_request(sync_token="tok0")
        second_page = _candidates_request(cursor="c1", sync_token="tok0")
        with HttpMocker() as http_mocker:
            http_mocker.post(
                first_page,
                _page(
                    [{"id": "candidate-1"}],
                    more_data_available=True,
                    next_cursor="c1",
                    sync_token="tok0",
                ),
            )
            http_mocker.post(
                second_page,
                _page([{"id": "candidate-2"}], more_data_available=False, sync_token="tok2"),
            )

            output = _read(_cursor_state("tok0"))

        assert output.errors == []
        assert len(output.records) == 2
        assert output.most_recent_state.stream_state.__dict__["token"] == "tok2"
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    def test_empty_terminal_page_commits_its_token(self):
        request = _candidates_request(sync_token="tok0")
        with HttpMocker() as http_mocker:
            http_mocker.post(
                request,
                _page([], more_data_available=False, sync_token="tok3"),
            )

            output = _read(_cursor_state("tok0"))

        assert output.errors == []
        assert output.records == []
        assert output.most_recent_state.stream_state.__dict__["token"] == "tok3"
        http_mocker.assert_number_of_calls(request, 1)

    def test_expired_token_fails_the_stream_and_keeps_the_stored_token(self):
        token_request = _candidates_request(sync_token="tok_old")
        with HttpMocker() as http_mocker:
            http_mocker.post(token_request, _error("sync_token_expired", "Token expired"))

            output = _read(_cursor_state("tok_old"))

        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert "sync_token_expired" in error.message
        assert "Refresh this stream" in error.message
        assert all(token == "tok_old" for token in _emitted_tokens(output))
        http_mocker.assert_number_of_calls(token_request, 1)

    def test_non_token_error_mid_pagination_does_not_replace_the_committed_token(self):
        first_page = _candidates_request(sync_token="tok0")
        second_page = _candidates_request(cursor="c1", sync_token="tok0")
        with HttpMocker() as http_mocker:
            http_mocker.post(
                first_page,
                _page([{"id": "candidate-1"}], more_data_available=True, next_cursor="c1"),
            )
            http_mocker.post(second_page, _error("some_other_error", "x"))

            output = _read(_cursor_state("tok0"))

        assert output.errors
        assert all(token == "tok0" for token in _emitted_tokens(output))
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    def test_discovery_declares_candidates_incremental_cursor(self):
        config = ConfigBuilder().build()
        catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)
        streams_by_name = {stream.name: stream for stream in catalog.streams}
        stream = streams_by_name[_STREAM_NAME]

        assert SyncMode.incremental in stream.supported_sync_modes
        assert stream.source_defined_cursor is True
        assert stream.default_cursor_field == ["updatedAt"]
