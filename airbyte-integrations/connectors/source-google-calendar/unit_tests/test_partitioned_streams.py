#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Mock-server tests for the streams partitioned over calendars: `events`, `acl` and `freebusy`.

With `calendarid` set, the only partition is that calendar, read through `calendars/{id}` so the
`primary` alias resolves to the real id and the calendar list is never requested. With it unset,
every calendar in the list is a partition, hidden ones included, narrowed per stream by the
account's access role: `events` reads calendars it can read, `acl` calendars it owns, `freebusy`
every calendar. Calendar ids are URL-encoded in paths (holiday calendars contain `#`). `events`
keeps one cursor for every calendar.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Optional

import freezegun
import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_BASE_URL = "https://www.googleapis.com/calendar/v3"
_TOKEN_REQUEST = HttpRequest(
    "https://oauth2.googleapis.com/token",
    body="grant_type=refresh_token&client_id=id&client_secret=secret&refresh_token=rt",
)
_TOKEN_RESPONSE = HttpResponse(json.dumps({"access_token": "at", "expires_in": 3600}))
_CONFIG = {"client_id": "id", "client_secret": "secret", "client_refresh_token_2": "rt"}
_EVENTS_PARAMS = {"showDeleted": "true", "maxResults": "2500", "singleEvents": "false"}
_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

_ME = "me@x.com"
_HOLIDAYS = "en.usa#holiday@group.v.calendar.google.com"
_ENCODED = {_ME: "me%40x.com", _HOLIDAYS: "en.usa%23holiday%40group.v.calendar.google.com"}


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _days_ago(n: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime(_DATETIME_FORMAT)


def _config(**overrides) -> Mapping[str, Any]:
    return {**_CONFIG, **overrides}


def _json(body: Any, status_code: int = 200) -> HttpResponse:
    return HttpResponse(json.dumps(body), status_code=status_code)


def _error(status_code: int, reason: str) -> HttpResponse:
    return _json({"error": {"code": status_code, "message": "error", "errors": [{"reason": reason, "domain": "global"}]}}, status_code)


def _mock_calendar_list(http_mocker: HttpMocker, *calendar_ids: str, min_access_role: Optional[str] = None) -> HttpRequest:
    params = {"showHidden": "true"}
    if min_access_role:
        params["minAccessRole"] = min_access_role
    request = HttpRequest(f"{_BASE_URL}/users/me/calendarList", query_params=params)
    http_mocker.get(request, _json({"kind": "calendar#calendarList", "items": [{"id": c} for c in calendar_ids]}))
    return request


def _events_request(calendar_id: str, updated_min: Optional[str] = None) -> HttpRequest:
    params = dict(_EVENTS_PARAMS)
    if updated_min is not None:
        params["updatedMin"] = updated_min
    return HttpRequest(f"{_BASE_URL}/calendars/{_ENCODED.get(calendar_id, calendar_id)}/events", query_params=params)


def _read(http_mocker: HttpMocker, stream: str, sync_mode: SyncMode, config: Mapping[str, Any], state=None):
    http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    return read(get_source(config, state=state), config, catalog, state=state)


def _stream_state(output) -> Mapping[str, Any]:
    return json.loads(json.dumps(output.state_messages[-1].state.stream.stream_state, default=lambda o: o.__dict__))


# --- partitions ---------------------------------------------------------------------------


def test_events_read_every_calendar_when_calendarid_is_unset():
    with HttpMocker() as http_mocker:
        _mock_calendar_list(http_mocker, _ME, _HOLIDAYS, min_access_role="reader")
        http_mocker.get(_events_request(_ME), _json({"items": [{"id": "e1", "updated": _days_ago(1)}]}))
        http_mocker.get(_events_request(_HOLIDAYS), _json({"items": [{"id": "e1", "updated": _days_ago(3)}]}))

        output = _read(http_mocker, "events", SyncMode.incremental, _config())

        assert output.errors == []
        # The same event id on two calendars stays two rows: the primary key includes the calendar.
        assert sorted((r.record.data["calendar_id"], r.record.data["id"]) for r in output.records) == [
            (_HOLIDAYS, "e1"),
            (_ME, "e1"),
        ]
        state = _stream_state(output)
        assert state["use_global_cursor"] is True
        assert "states" not in state or state["states"] == []


def test_configured_calendar_resolves_the_primary_alias_without_reading_the_calendar_list():
    # HttpMocker fails on any unmocked request, so an extra calendarList call would fail this test.
    with HttpMocker() as http_mocker:
        http_mocker.get(HttpRequest(f"{_BASE_URL}/calendars/primary"), _json({"kind": "calendar#calendar", "id": _ME}))
        http_mocker.get(_events_request(_ME), _json({"items": [{"id": "e1", "updated": _days_ago(1)}]}))

        output = _read(http_mocker, "events", SyncMode.full_refresh, _config(calendarid="primary"))

        assert output.errors == []
        assert [r.record.data["calendar_id"] for r in output.records] == [_ME]


def test_every_calendar_sends_the_global_cursor_so_a_quiet_calendar_is_not_stale():
    cursor = _days_ago(2)
    state = (
        StateBuilder().with_stream_state("events", {"use_global_cursor": True, "state": {"updated": cursor}, "lookback_window": 0}).build()
    )
    with HttpMocker() as http_mocker:
        _mock_calendar_list(http_mocker, _ME, _HOLIDAYS, min_access_role="reader")
        me = _events_request(_ME, updated_min=cursor)
        holidays = _events_request(_HOLIDAYS, updated_min=cursor)
        http_mocker.get(me, _json({"items": [{"id": "e2", "updated": _days_ago(1)}]}))
        http_mocker.get(holidays, _json({"items": []}))

        output = _read(http_mocker, "events", SyncMode.incremental, _config(), state=state)

        assert output.errors == []
        http_mocker.assert_number_of_calls(me, 1)
        http_mocker.assert_number_of_calls(holidays, 1)


def test_events_primary_key_includes_the_calendar():
    catalog = get_source(_config()).discover(logger=None, config=_config())
    events = next(stream for stream in catalog.streams if stream.name == "events")
    assert events.source_defined_primary_key == [["calendar_id"], ["id"]]


def test_configured_calendar_ignores_the_access_role_filter():
    # With calendarid set, acl reads that calendar directly, whatever the account's role on it.
    with HttpMocker() as http_mocker:
        http_mocker.get(HttpRequest(f"{_BASE_URL}/calendars/{_ENCODED[_ME]}"), _json({"kind": "calendar#calendar", "id": _ME}))
        http_mocker.get(_acl_request(_ME), _json({"items": [{"id": "user:a"}]}))

        output = _read(http_mocker, "acl", SyncMode.full_refresh, _config(calendarid=_ME))

        assert output.errors == []
        assert [r.record.data["id"] for r in output.records] == ["user:a"]


# --- acl ----------------------------------------------------------------------------------


def _acl_request(calendar_id: str, page_token: Optional[str] = None) -> HttpRequest:
    params = {"maxResults": "250"}
    if page_token:
        params["pageToken"] = page_token
    return HttpRequest(f"{_BASE_URL}/calendars/{_ENCODED[calendar_id]}/acl", query_params=params)


def test_acl_paginates_and_adds_calendar_id():
    with HttpMocker() as http_mocker:
        _mock_calendar_list(http_mocker, _ME, min_access_role="owner")
        http_mocker.get(_acl_request(_ME), _json({"items": [{"id": "user:a"}], "nextPageToken": "p2"}))
        http_mocker.get(_acl_request(_ME, page_token="p2"), _json({"items": [{"id": "user:b"}]}))

        output = _read(http_mocker, "acl", SyncMode.full_refresh, _config())

        assert output.errors == []
        assert [(r.record.data["calendar_id"], r.record.data["id"]) for r in output.records] == [(_ME, "user:a"), (_ME, "user:b")]


@pytest.mark.parametrize(("status_code", "reason"), [(403, "forbidden"), (404, "notFound")])
def test_acl_of_a_calendar_the_account_does_not_own_is_skipped(status_code, reason):
    with HttpMocker() as http_mocker:
        _mock_calendar_list(http_mocker, _ME, _HOLIDAYS, min_access_role="owner")
        http_mocker.get(_acl_request(_ME), _json({"items": [{"id": "user:a"}]}))
        http_mocker.get(_acl_request(_HOLIDAYS), _error(status_code, reason))

        output = _read(http_mocker, "acl", SyncMode.full_refresh, _config())

        assert output.errors == []
        assert [r.record.data["id"] for r in output.records] == ["user:a"]


@pytest.mark.parametrize("reason", ["insufficientPermissions", "accessNotConfigured"])
def test_acl_missing_scope_fails_with_a_config_error_naming_the_scope(reason):
    with HttpMocker() as http_mocker:
        _mock_calendar_list(http_mocker, _ME, min_access_role="owner")
        http_mocker.get(_acl_request(_ME), _error(403, reason))

        output = _read(http_mocker, "acl", SyncMode.full_refresh, _config())

        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert "calendar.acls.readonly" in error.message


def test_acl_quota_403_is_not_ignored():
    with HttpMocker() as http_mocker:
        _mock_calendar_list(http_mocker, _ME, min_access_role="owner")
        http_mocker.get(_acl_request(_ME), _error(403, "quotaExceeded"))

        output = _read(http_mocker, "acl", SyncMode.full_refresh, _config())

        assert output.errors[0].trace.error.failure_type == FailureType.transient_error


def test_acl_rate_limit_403_is_retried():
    with HttpMocker() as http_mocker:
        _mock_calendar_list(http_mocker, _ME, min_access_role="owner")
        request = _acl_request(_ME)
        http_mocker.get(request, [_error(403, "rateLimitExceeded"), _json({"items": [{"id": "user:a"}]})])

        output = _read(http_mocker, "acl", SyncMode.full_refresh, _config())

        assert output.errors == []
        assert [r.record.data["id"] for r in output.records] == ["user:a"]
        http_mocker.assert_number_of_calls(request, 2)


# --- freebusy -----------------------------------------------------------------------------


def _freebusy_request(calendar_id: str) -> HttpRequest:
    return HttpRequest(
        f"{_BASE_URL}/freeBusy",
        body=json.dumps({"timeMin": "2026-09-07T12:00:00Z", "timeMax": "2026-11-21T12:00:00Z", "items": [{"id": calendar_id}]}),
    )


@freezegun.freeze_time("2026-10-07T12:00:00Z")
def test_freebusy_queries_a_fixed_window_and_ignores_start_date():
    busy = [{"start": "2026-10-08T09:00:00Z", "end": "2026-10-08T10:00:00Z"}]
    with HttpMocker() as http_mocker:
        _mock_calendar_list(http_mocker, _ME)
        http_mocker.post(_freebusy_request(_ME), _json({"calendars": {_ME: {"busy": busy}}}))

        output = _read(http_mocker, "freebusy", SyncMode.full_refresh, _config(start_date="2020-01-01T00:00:00Z"))

        assert output.errors == []
        assert [r.record.data for r in output.records] == [{**busy[0], "calendar_id": _ME}]


@freezegun.freeze_time("2026-10-07T12:00:00Z")
def test_freebusy_per_calendar_error_is_logged():
    with HttpMocker() as http_mocker:
        _mock_calendar_list(http_mocker, _ME)
        http_mocker.post(
            _freebusy_request(_ME),
            _json({"calendars": {_ME: {"errors": [{"domain": "global", "reason": "notFound"}], "busy": []}}}),
        )

        output = _read(http_mocker, "freebusy", SyncMode.full_refresh, _config())

        assert output.errors == []
        assert output.records == []
        assert any("could not compute free/busy" in log.log.message for log in output.logs)


# --- calendars and colors -----------------------------------------------------------------


def test_calendars_reads_the_calendar_resource_of_every_readable_listed_calendar():
    with HttpMocker() as http_mocker:
        # Same calendars as `calendarlist` (no showHidden), narrowed to ones the account can read.
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/users/me/calendarList", query_params={"minAccessRole": "reader"}),
            _json(
                {"kind": "calendar#calendarList", "items": [{"id": _ME, "accessRole": "owner"}, {"id": _HOLIDAYS, "accessRole": "reader"}]}
            ),
        )
        for calendar_id in (_ME, _HOLIDAYS):
            http_mocker.get(
                HttpRequest(f"{_BASE_URL}/calendars/{_ENCODED[calendar_id]}"),
                _json({"kind": "calendar#calendar", "id": calendar_id, "summary": calendar_id, "timeZone": "UTC"}),
            )

        output = _read(http_mocker, "calendars", SyncMode.full_refresh, _config(calendarid=_ME))

        assert output.errors == []
        assert sorted(r.record.data["id"] for r in output.records) == [_HOLIDAYS, _ME]
        assert {r.record.data["kind"] for r in output.records} == {"calendar#calendar"}
        assert all("accessRole" not in r.record.data for r in output.records)


def test_colors_primary_key_is_the_scalar_kind():
    catalog = get_source(_config()).discover(logger=None, config=_config())
    colors = next(stream for stream in catalog.streams if stream.name == "colors")
    assert colors.source_defined_primary_key == [["kind"]]


@pytest.mark.parametrize(
    ("stream", "path", "fmt"),
    [
        ("events", ["updated"], "date-time"),
        ("events", ["created"], "date-time"),
        ("events", ["start", "dateTime"], "date-time"),
        ("events", ["start", "date"], "date"),
        ("events", ["end", "dateTime"], "date-time"),
        ("events", ["end", "date"], "date"),
        ("events", ["originalStartTime", "dateTime"], "date-time"),
        ("events", ["originalStartTime", "date"], "date"),
        ("colors", ["updated"], "date-time"),
        ("freebusy", ["start"], "date-time"),
        ("freebusy", ["end"], "date-time"),
    ],
)
def test_date_and_datetime_fields_are_typed(stream, path, fmt):
    catalog = get_source(_config()).discover(logger=None, config=_config())
    node = next(s for s in catalog.streams if s.name == stream).json_schema
    for key in path:
        node = node["properties"][key]
    assert node["format"] == fmt
    if fmt == "date-time":
        assert node["airbyte_type"] == "timestamp_with_timezone"
