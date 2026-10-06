#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Mock-server tests for the `events` stream: updatedMin bounding and error handling.

Google rejects `updatedMin` bounds older than ~30 days with a 410, so `events` is a
`StateDelegatingStream` with `api_retention_period: P28D`: with no saved cursor, or one
older than 28 days, the full-refresh stream re-reads the calendar without `updatedMin`
(clearing the stale state first); otherwise the incremental stream sends `updatedMin`.
These tests pin the exact request parameters per case and the failure classification
of 403/410 responses.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Optional

import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "client_id": "id",
    "client_secret": "secret",
    "client_refresh_token_2": "rt",
    "calendarid": "primary",
}

_TOKEN_URL = "https://oauth2.googleapis.com/token"
_TOKEN_REQUEST = HttpRequest(
    _TOKEN_URL,
    body="grant_type=refresh_token&client_id=id&client_secret=secret&refresh_token=rt",
)
_TOKEN_RESPONSE = HttpResponse(json.dumps({"access_token": "at", "expires_in": 3600}))
_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
_BASE_PARAMS = {"showDeleted": "true", "maxResults": "2500", "singleEvents": "false"}
_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
_RECORD = {"id": "e1", "updated": "2026-09-25T12:00:00.000000Z"}


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _events_request(updated_min: Optional[str] = None) -> HttpRequest:
    params = dict(_BASE_PARAMS)
    if updated_min is not None:
        params["updatedMin"] = updated_min
    return HttpRequest(_EVENTS_URL, query_params=params)


def _items_response(*records) -> HttpResponse:
    return HttpResponse(json.dumps({"items": list(records)}))


def _catalog(sync_mode: SyncMode) -> Any:
    return CatalogBuilder().with_stream("events", sync_mode).build()


def _config(**overrides) -> Mapping[str, Any]:
    config = dict(_CONFIG)
    config.update(overrides)
    return config


def _read_events(http_mocker: HttpMocker, sync_mode: SyncMode, state=None, expecting_exception=False):
    http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
    config = _config()
    source = get_source(config, state=state)
    return read(source, config, _catalog(sync_mode), state=state, expecting_exception=expecting_exception)


def _days_ago(n: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime(_DATETIME_FORMAT)


def _stream_state(state_message) -> Mapping[str, Any]:
    return json.loads(json.dumps(state_message.state.stream.stream_state, default=lambda o: o.__dict__))


def _error_trace(output):
    assert output.errors, "expected the sync to emit an error trace message"
    return output.errors[0].trace.error


def test_full_refresh_no_state_sends_no_updated_min():
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, _items_response(_RECORD))
        http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)

        output = read(get_source(_config()), _config(), _catalog(SyncMode.full_refresh))

        assert output.errors == []
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(request, 1)


def test_incremental_no_state_no_start_date_sends_no_updated_min():
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, _items_response(_RECORD))

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)


def test_incremental_fresh_state_sends_updated_min():
    cursor = _days_ago(2)
    state = StateBuilder().with_stream_state("events", {"updated": cursor}).build()
    with HttpMocker() as http_mocker:
        request = _events_request(updated_min=cursor)
        http_mocker.get(request, _items_response(_RECORD))

        output = _read_events(http_mocker, SyncMode.incremental, state=state)

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)


def test_incremental_stale_state_drops_updated_min_and_resets_state():
    state = StateBuilder().with_stream_state("events", {"updated": _days_ago(60)}).build()
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, _items_response(_RECORD))

        output = _read_events(http_mocker, SyncMode.incremental, state=state)

        assert output.errors == []
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(request, 1)
        emitted_states = [_stream_state(message) for message in output.state_messages]
        assert emitted_states[0] == {}, "the stale cursor is cleared before the full re-read"
        assert _RECORD["updated"] in emitted_states[-1].get("updated", "")


def test_incremental_stale_start_date_drops_updated_min():
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, _items_response(_RECORD))
        http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
        config = _config(start_date=_days_ago(60))

        output = read(get_source(config), config, _catalog(SyncMode.incremental))

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)


def test_rate_limit_403_retries_then_succeeds():
    rate_limited = HttpResponse(json.dumps({"error": {"errors": [{"reason": "userRateLimitExceeded"}], "code": 403}}), status_code=403)
    with HttpMocker() as http_mocker:
        request = _events_request()
        http_mocker.get(request, [rate_limited, _items_response(_RECORD)])

        output = _read_events(http_mocker, SyncMode.incremental)

        assert output.errors == []
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(request, 2)


def test_plain_403_fails_as_config_error():
    with HttpMocker() as http_mocker:
        http_mocker.get(_events_request(), HttpResponse(json.dumps({"error": {"code": 403, "message": "Forbidden"}}), status_code=403))

        output = _read_events(http_mocker, SyncMode.incremental, expecting_exception=True)

        error = _error_trace(output)
        assert error.failure_type == FailureType.config_error
        assert "lacks access to the configured calendar" in error.message


def test_410_fails_as_config_error_with_remediation():
    cursor = _days_ago(2)
    state = StateBuilder().with_stream_state("events", {"updated": cursor}).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _events_request(updated_min=cursor),
            HttpResponse(json.dumps({"error": {"code": 410, "errors": [{"reason": "updatedMinTooLongAgo"}]}}), status_code=410),
        )
        http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
        config = _config()

        output = read(get_source(config, state=state), config, _catalog(SyncMode.incremental), state=state, expecting_exception=True)

        error = _error_trace(output)
        assert error.failure_type == FailureType.config_error
        assert "roughly the last 30 days" in error.message


def test_cancelled_record_is_emitted_and_does_not_move_cursor():
    cancelled = {"id": "x", "status": "cancelled"}
    record = {"id": "e1", "updated": _days_ago(1)}
    cursor = _days_ago(5)
    cursor_state = StateBuilder().with_stream_state("events", {"updated": cursor}).build()
    with HttpMocker() as http_mocker:
        request = _events_request(updated_min=cursor)
        http_mocker.get(request, _items_response(cancelled, record))
        http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
        config = _config()

        output = read(get_source(config, state=cursor_state), config, _catalog(SyncMode.incremental), state=cursor_state)

        assert output.errors == []
        assert len(output.records) == 2
        assert record["updated"] in _stream_state(output.state_messages[-1])["updated"]
