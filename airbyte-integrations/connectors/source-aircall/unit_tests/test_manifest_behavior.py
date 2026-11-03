# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
import re
from datetime import datetime

import pytest
import yaml
from freezegun import freeze_time
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_BASE_URL = "https://api.aircall.io/v1"
_CONFIG = {"api_id": "test-id", "api_token": "test-token"}
_NOW = "2026-11-03T00:00:00Z"
_WINDOW_SECONDS = 86400
_CONTACTS_EPOCH = 1388534400


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    sleeps = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: sleeps.append(seconds))
    return sleeps


def _sleep_moves_clock(clock, monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Make time.sleep move the frozen clock (at least 1 ms, as real time would) and record each wait."""
    sleeps = []

    def _sleep(seconds=0, *_args, **_kwargs):
        sleeps.append(seconds)
        clock.tick(max(seconds, 0.001))

    monkeypatch.setattr("time.sleep", _sleep)
    return sleeps


def _epoch(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def _request(path: str, query_params: dict[str, str] | None = None) -> HttpRequest:
    return HttpRequest(f"{_BASE_URL}{path}", query_params=query_params or {})


def _read_stream(
    stream_name: str,
    sync_mode: SyncMode,
    config: dict | None = None,
    state=None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    selected_config = config or _CONFIG
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(
        get_source(config=selected_config, state=state),
        config=selected_config,
        catalog=catalog,
        state=state,
        expecting_exception=expecting_exception,
    )


def _response(stream_name: str, records: list[dict]) -> HttpResponse:
    return HttpResponse(body=json.dumps({stream_name: records}), status_code=200)


def _call_requests(start: int, end: int, window_days: int = 1) -> list[tuple[int, int]]:
    requests = []
    window_seconds = window_days * _WINDOW_SECONDS
    while start < end:
        next_start = min(start + window_seconds, end)
        window_end = next_start if next_start == end else next_start - 1
        requests.append((start, window_end))
        start = next_start
    return requests


def _call_record(started_at: int, call_id: int) -> dict:
    return {"id": call_id, "started_at": started_at, "sid": f"sid-{call_id}"}


# Real body of Aircall's answer to page 201 of an oversized query (airbytehq/airbyte#76489).
_RESULT_CAP_BODY = {
    "error": "Bad Request",
    "data": None,
    "message": "BAD_REQUEST",
    "errors": "Your query is limited to 10k results and pagination is out of bound, please use timestamps or other filters.",
    "troubleshoot": "BAD_REQUEST",
    "success": False,
}


def _result_cap_response() -> HttpResponse:
    return HttpResponse(body=json.dumps(_RESULT_CAP_BODY), status_code=400)


def _error_trace(output: EntrypointOutput):
    assert output.errors
    return output.errors[0].trace.error


def test_calls_incremental_windows_pagination_and_state() -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        state_time = _epoch("2026-10-31T00:00:00Z")
        start = state_time - 3 * _WINDOW_SECONDS
        end = _epoch(_NOW)
        windows = _call_requests(start, end)
        state = StateBuilder().with_stream_state("calls", {"started_at": str(state_time)}).build()
        requests = []

        for index, (window_start, window_end) in enumerate(windows):
            first_page = (
                [_call_record(window_start + 1, call_id) for call_id in range(1, 51)]
                if index == 0
                else [_call_record(window_start + 1, index + 1)]
            )
            first_request = _request("/calls", {"from": str(window_start), "to": str(window_end), "per_page": "50"})
            second_request = None
            http_mocker.get(first_request, _response("calls", first_page))
            if index == 0:
                second_request = _request(
                    "/calls",
                    {"from": str(window_start), "to": str(window_end), "per_page": "50", "page": "2"},
                )
                http_mocker.get(second_request, _response("calls", [_call_record(window_start + 2, 51)]))
            requests.append((first_request, second_request))

        output = _read_stream(
            "calls",
            SyncMode.incremental,
            config={**_CONFIG, "window_in_days": 1},
            state=state,
        )

        assert output.errors == []
        assert len(output.records) == 50 + 1 + len(windows) - 1
        assert output.most_recent_state.stream_state.started_at == str(windows[-1][0] + 1)
        for first_request, second_request in requests:
            http_mocker.assert_number_of_calls(first_request, 1)
            if second_request:
                http_mocker.assert_number_of_calls(second_request, 1)


def test_calls_default_window_reads_186_daily_windows_within_the_rate_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    with freeze_time(_NOW) as clock, HttpMocker() as http_mocker:
        sleeps = _sleep_moves_clock(clock, monkeypatch)
        end = _epoch(_NOW)
        windows = _call_requests(end - 186 * _WINDOW_SECONDS, end)
        requests = [_request("/calls", {"from": str(start), "to": str(stop), "per_page": "50"}) for start, stop in windows]
        for request in requests:
            http_mocker.get(request, _response("calls", []))

        # One worker, so a single thread waits for the budget and the waits add up deterministically.
        output = _read_stream("calls", SyncMode.full_refresh, config={**_CONFIG, "num_workers": 1})

        assert output.errors == []
        assert len(requests) == 186
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)
        # 120 requests per minute: the 121st waits for the window to move on.
        assert 59 <= sum(sleeps) <= 61


def test_calls_full_refresh_starts_at_now_minus_186_days() -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        start = _epoch(_NOW) - 186 * _WINDOW_SECONDS
        end = _epoch(_NOW)
        request = _request("/calls", {"from": str(start), "to": str(end), "per_page": "50"})
        http_mocker.get(request, _response("calls", [_call_record(start, 1)]))

        output = _read_stream(
            "calls",
            SyncMode.full_refresh,
            config={**_CONFIG, "window_in_days": 365},
        )

        assert output.errors == []
        assert [record.record.data["started_at"] for record in output.records] == [start]
        http_mocker.assert_number_of_calls(request, 1)


def test_contacts_use_configured_date_windows() -> None:
    with freeze_time("2014-01-03T00:00:00Z"), HttpMocker() as http_mocker:
        windows = 2
        requests = []
        for index in range(windows):
            window_start = _CONTACTS_EPOCH + index * 2 * _WINDOW_SECONDS
            window_end = window_start + 2 * _WINDOW_SECONDS - 1
            request = _request(
                "/contacts",
                {"from": str(window_start), "to": str(window_end), "per_page": "50"},
            )
            requests.append(request)
            http_mocker.get(request, _response("contacts", [{"id": index + 1}]))

        output = _read_stream("contacts", SyncMode.full_refresh, config={**_CONFIG, "window_in_days": 2})

        assert output.errors == []
        assert len(output.records) == windows
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)


def test_contacts_default_window_count_is_thirty_days() -> None:
    with freeze_time("2014-03-01T00:00:00Z"), HttpMocker() as http_mocker:
        window_count = 2
        requests = []
        for index in range(window_count):
            window_start = _CONTACTS_EPOCH + index * 30 * _WINDOW_SECONDS
            window_end = window_start + 30 * _WINDOW_SECONDS - 1
            request = _request(
                "/contacts",
                {"from": str(window_start), "to": str(window_end), "per_page": "50"},
            )
            requests.append(request)
            http_mocker.get(request, _response("contacts", [{"id": index + 1}]))

        output = _read_stream("contacts", SyncMode.full_refresh)

        assert output.errors == []
        assert len(output.records) == window_count
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("numbers", id="numbers"),
        pytest.param("teams", id="teams"),
    ],
)
def test_numbers_and_teams_emit_records_with_past_state(stream_name: str) -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        request = _request(f"/{stream_name}", {"per_page": "50"})
        http_mocker.get(
            request,
            _response(
                stream_name,
                [
                    {"id": 1, "created_at": "2023-10-03T18:35:43.000Z"},
                    {"id": 2, "created_at": "2025-10-03T18:35:43Z"},
                ],
            ),
        )
        state = StateBuilder().with_stream_state(stream_name, {"created_at": "2025-06-01T00:00:00.000Z"}).build()

        output = _read_stream(stream_name, SyncMode.incremental, state=state)

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)
        assert [record.record.data["id"] for record in output.records] == [1, 2]
        assert output.most_recent_state.stream_state.created_at == "2025-10-03T18:35:43.000000+0000"


@pytest.mark.parametrize(
    "status_code,message",
    [
        pytest.param(
            401,
            "Aircall rejected the API ID and API token (HTTP 401). Create a new API key in the Aircall Dashboard "
            "(Integrations & API > API Keys, https://dashboard.aircall.io/integrations/api-keys) and update the connector.",
            id="401",
        ),
        pytest.param(
            403,
            "Aircall returned HTTP 403 for https://api.aircall.io/v1/calls. Check that the API ID and API token are valid "
            "(Integrations & API > API Keys, https://dashboard.aircall.io/integrations/api-keys) and that your Aircall "
            "plan includes this data.",
            id="403",
        ),
    ],
)
def test_401_and_403_are_config_errors_with_actionable_message(status_code: int, message: str) -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        start = _epoch(_NOW) - 186 * _WINDOW_SECONDS
        request = _request("/calls", {"from": str(start), "to": str(_epoch(_NOW)), "per_page": "50"})
        http_mocker.get(request, HttpResponse(body='{"message":"Forbidden"}', status_code=status_code))

        output = _read_stream(
            "calls",
            SyncMode.full_refresh,
            config={**_CONFIG, "window_in_days": 365},
            expecting_exception=True,
        )

        error = _error_trace(output)
        assert error.failure_type == FailureType.config_error
        assert error.message == message
        http_mocker.assert_number_of_calls(request, 1)


def test_calls_split_a_window_that_hits_the_result_cap() -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        start = _epoch(_NOW) - 186 * _WINDOW_SECONDS
        end = _epoch(_NOW)
        first_end = start + (end - start + 1) // 2 - 1
        oversized = _request("/calls", {"from": str(start), "to": str(end), "per_page": "50"})
        first_half = _request("/calls", {"from": str(start), "to": str(first_end), "per_page": "50"})
        second_half = _request("/calls", {"from": str(first_end + 1), "to": str(end), "per_page": "50"})
        http_mocker.get(oversized, _result_cap_response())
        http_mocker.get(first_half, _response("calls", [_call_record(start, 1)]))
        http_mocker.get(second_half, _response("calls", [_call_record(end, 2)]))

        output = _read_stream("calls", SyncMode.full_refresh, config={**_CONFIG, "window_in_days": 365})

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == [1, 2]
        for request in (oversized, first_half, second_half):
            http_mocker.assert_number_of_calls(request, 1)


def test_contacts_result_cap_is_a_config_error() -> None:
    with freeze_time("2014-01-03T00:00:00Z"), HttpMocker() as http_mocker:
        request = _request(
            "/contacts",
            {"from": str(_CONTACTS_EPOCH), "to": str(_CONTACTS_EPOCH + 30 * _WINDOW_SECONDS - 1), "per_page": "50"},
        )
        http_mocker.get(request, _result_cap_response())

        output = _read_stream("contacts", SyncMode.full_refresh, expecting_exception=True)

        error = _error_trace(output)
        assert error.failure_type == FailureType.config_error
        assert error.message == (
            "Aircall returns at most 10,000 contacts per request window. "
            "Lower the Window size (days) setting (minimum 1) so each window holds fewer than 10,000 contacts."
        )
        http_mocker.assert_number_of_calls(request, 1)


def test_other_400_errors_keep_the_default_classification() -> None:
    with freeze_time("2014-01-03T00:00:00Z"), HttpMocker() as http_mocker:
        request = _request(
            "/contacts",
            {"from": str(_CONTACTS_EPOCH), "to": str(_CONTACTS_EPOCH + 30 * _WINDOW_SECONDS - 1), "per_page": "50"},
        )
        body = {**_RESULT_CAP_BODY, "errors": "from must be lower than to"}
        http_mocker.get(request, HttpResponse(body=json.dumps(body), status_code=400))

        output = _read_stream("contacts", SyncMode.full_refresh, expecting_exception=True)

        error = _error_trace(output)
        assert error.failure_type == FailureType.system_error
        assert "10,000" not in error.message
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("unit", [pytest.param(1, id="seconds"), pytest.param(1000, id="milliseconds")])
def test_429_waits_until_the_reset_header_then_reads_records(monkeypatch: pytest.MonkeyPatch, unit: int) -> None:
    with freeze_time(_NOW) as clock, HttpMocker() as http_mocker:
        sleeps = _sleep_moves_clock(clock, monkeypatch)
        start = _epoch(_NOW) - 186 * _WINDOW_SECONDS
        request = _request("/calls", {"from": str(start), "to": str(_epoch(_NOW)), "per_page": "50"})
        http_mocker.get(
            request,
            [
                HttpResponse(
                    body='{"message":"rate limited"}',
                    status_code=429,
                    headers={
                        "X-AircallApi-Limit": "120",
                        "X-AircallApi-Remaining": "0",
                        "X-AircallApi-Reset": str((_epoch(_NOW) + 30) * unit),
                    },
                ),
                _response("calls", [_call_record(start, 1)]),
            ],
        )

        output = _read_stream(
            "calls",
            SyncMode.full_refresh,
            config={**_CONFIG, "window_in_days": 365},
        )

        assert output.errors == []
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(request, 2)
        # 30 s until the reset, plus the second the CDK adds to every wait taken from a header.
        assert sleeps[0] == 31.0


def test_500_without_reset_header_retries_with_fallback_backoff(monkeypatch: pytest.MonkeyPatch) -> None:
    with freeze_time(_NOW) as clock, HttpMocker() as http_mocker:
        sleeps = _sleep_moves_clock(clock, monkeypatch)
        start = _epoch(_NOW) - 186 * _WINDOW_SECONDS
        request = _request("/calls", {"from": str(start), "to": str(_epoch(_NOW)), "per_page": "50"})
        http_mocker.get(
            request,
            [
                HttpResponse(body='{"message":"server error"}', status_code=500),
                _response("calls", [_call_record(start, 1)]),
            ],
        )

        output = _read_stream(
            "calls",
            SyncMode.full_refresh,
            config={**_CONFIG, "window_in_days": 365},
        )

        assert output.errors == []
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(request, 2)
        assert sleeps == [1]


def test_check_requests_only_company() -> None:
    company_request = _request("/company")
    with HttpMocker() as http_mocker:
        http_mocker.get(company_request, HttpResponse(body='{"company":{}}', status_code=200))

        status = get_source(config=_CONFIG).check(logging.getLogger("aircall-test"), _CONFIG)

        assert status.status == Status.SUCCEEDED
        http_mocker.assert_number_of_calls(company_request, 1)


def test_user_availability_paginates_and_emits_schema_fields() -> None:
    first_request = _request("/users/availabilities", {"per_page": "50"})
    second_request = _request("/users/availabilities", {"per_page": "50", "page": "2"})
    with HttpMocker() as http_mocker:
        http_mocker.get(first_request, _response("users", [{"id": 1, "availability": "available"}] * 50))
        http_mocker.get(second_request, _response("users", [{"id": 51, "availability": "unavailable"}]))

        output = _read_stream("user_availability", SyncMode.full_refresh)

        assert output.errors == []
        assert len(output.records) == 51
        assert output.records[0].record.data["id"] == 1
        assert output.records[0].record.data["availability"] == "available"
        assert output.records[-1].record.data["id"] == 51
        assert output.records[-1].record.data["availability"] == "unavailable"
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)


def _webhook(index: int) -> dict:
    return {"id": index, "webhook_id": f"9d3b6a0e-1f2c-4c5d-8e7f-{index:012d}", "custom_name": "Webhook"}


def test_webhooks_include_webhook_id_and_start_pagination_at_page_two() -> None:
    first_request = _request("/webhooks", {"per_page": "50"})
    second_request = _request("/webhooks", {"per_page": "50", "page": "2"})
    with HttpMocker() as http_mocker:
        http_mocker.get(first_request, _response("webhooks", [_webhook(index) for index in range(50)]))
        http_mocker.get(second_request, _response("webhooks", [_webhook(50)]))

        output = _read_stream("webhooks", SyncMode.full_refresh)

        assert output.errors == []
        assert len(output.records) == 51
        assert output.records[-1].record.data["webhook_id"] == "9d3b6a0e-1f2c-4c5d-8e7f-000000000050"
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("2022-03-01T00:00:00.000Z", id="fractional-seconds"),
        pytest.param("2022-03-01T00:00:00Z", id="whole-seconds"),
    ],
)
def test_start_date_pattern_accepts_milliseconds_and_whole_seconds(value: str) -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    pattern = manifest["spec"]["connection_specification"]["properties"]["start_date"]["pattern"]

    assert re.fullmatch(pattern, value)


_DOCUMENTED_FIELDS = {
    "calls": {"sid", "conference_participants"},
    "contacts": {"description"},
    "tags": {"direct_link"},
    "user_availability": {"id", "availability"},
    "users": {"substatus", "extension", "default_number_id"},
    "webhooks": {"webhook_id", "custom_name"},
}


def test_discovered_schemas_declare_primary_keys_and_documented_fields() -> None:
    catalog = get_source(config=_CONFIG).discover(logging.getLogger("aircall-test"), _CONFIG)
    schemas = {stream.name: stream.json_schema["properties"] for stream in catalog.streams}

    for stream in catalog.streams:
        for key in stream.source_defined_primary_key or []:
            assert key[0] in schemas[stream.name], (stream.name, key)
    for stream_name, fields in _DOCUMENTED_FIELDS.items():
        assert fields <= set(schemas[stream_name]), (stream_name, fields - set(schemas[stream_name]))
    assert "webhook_id" not in schemas["teams"]
