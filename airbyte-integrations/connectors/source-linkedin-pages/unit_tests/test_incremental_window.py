# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime
from urllib.parse import parse_qs, urlsplit

import pytest
import requests_mock
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "org_id": "12345678",
    "credentials": {"auth_method": "access_token", "access_token": "test_token"},
    "time_granularity_type": "DAY",
}
_BASE_URL = "https://api.linkedin.com/rest"
_STREAMS = {
    "follower_statistics_time_bound": "/organizationalEntityFollowerStatistics",
    "share_statistics_time_bound": "/organizationalEntityShareStatistics",
}
_DAY_MS = 86_400_000


def _milliseconds(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def _read(stream_name, config, response, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    url = f"{_BASE_URL}{_STREAMS[stream_name]}"
    with requests_mock.Mocker() as mocker:
        endpoint = mocker.get(url, json=response)
        output = read(get_source(config, state=state), config, catalog, state=state)

    return output, endpoint


def _query_params(request):
    return {key: values[0] for key, values in parse_qs(urlsplit(request.url).query).items()}


def _expected_query(stream_name, start_ms, end_ms, granularity="DAY"):
    return {
        "q": "organizationalEntity",
        "organizationalEntity": "urn:li:organization:12345678",
        "timeIntervals.timeGranularityType": granularity,
        "timeIntervals.timeRange.start": str(start_ms),
        "timeIntervals.timeRange.end": str(end_ms),
    }


@pytest.mark.parametrize("stream_name", list(_STREAMS))
@freeze_time("2026-10-23T14:37:12Z")
def test_first_sync_uses_midnight_aligned_available_window(stream_name):
    config = dict(_CONFIG)
    output, endpoint = _read(stream_name, config, {"elements": []})

    assert not output.errors
    assert endpoint.call_count == 1
    assert _query_params(endpoint.last_request) == _expected_query(
        stream_name,
        _milliseconds("2025-10-23T00:00:00Z"),
        _milliseconds("2026-10-21T00:00:00Z"),
    )


@pytest.mark.parametrize("stream_name", list(_STREAMS))
@freeze_time("2026-10-23T14:37:12Z")
def test_first_sync_honors_start_date_inside_available_window(stream_name):
    config = {**_CONFIG, "start_date": "2026-03-15T00:00:00Z"}
    output, endpoint = _read(stream_name, config, {"elements": []})

    assert not output.errors
    assert endpoint.call_count == 1
    assert _query_params(endpoint.last_request) == _expected_query(
        stream_name,
        _milliseconds("2026-03-15T00:00:00Z"),
        _milliseconds("2026-10-21T00:00:00Z"),
    )


@pytest.mark.parametrize("stream_name", list(_STREAMS))
@freeze_time("2026-10-23T14:37:12Z")
def test_first_sync_truncates_non_midnight_start_date_to_midnight(stream_name):
    config = {**_CONFIG, "start_date": "2026-03-15T14:22:05Z"}
    output, endpoint = _read(stream_name, config, {"elements": []})

    assert not output.errors
    assert endpoint.call_count == 1
    assert _query_params(endpoint.last_request) == _expected_query(
        stream_name,
        _milliseconds("2026-03-15T00:00:00Z"),
        _milliseconds("2026-10-21T00:00:00Z"),
    )


@pytest.mark.parametrize("stream_name", list(_STREAMS))
@freeze_time("2026-10-23T14:37:12Z")
def test_subsequent_sync_uses_midnight_cursor_and_whole_day_end(stream_name):
    cursor_ms = _milliseconds("2026-10-19T00:00:00Z")
    state = StateBuilder().with_stream_state(stream_name, {"timeRangeEnd": cursor_ms}).build()
    output, endpoint = _read(stream_name, _CONFIG, {"elements": []}, state)

    assert not output.errors
    assert endpoint.call_count == 1
    params = _query_params(endpoint.last_request)
    assert params == _expected_query(
        stream_name,
        cursor_ms,
        _milliseconds("2026-10-21T00:00:00Z"),
    )
    start_ms = int(params["timeIntervals.timeRange.start"])
    end_ms = int(params["timeIntervals.timeRange.end"])
    assert (end_ms - start_ms) % _DAY_MS == 0


@pytest.mark.parametrize("stream_name", list(_STREAMS))
def test_two_pass_reads_keep_second_window_midnight_aligned(stream_name):
    with freeze_time("2026-10-23T06:00:00Z") as frozen_time:
        start_ms = _milliseconds("2026-10-20T00:00:00Z")
        end_ms = _milliseconds("2026-10-21T00:00:00Z")
        first_output, first_endpoint = _read(
            stream_name,
            _CONFIG,
            {"elements": [{"timeRange": {"start": start_ms, "end": end_ms}}]},
        )
        assert not first_output.errors
        assert first_endpoint.call_count == 1
        first_params = _query_params(first_endpoint.last_request)
        assert first_params["timeIntervals.timeRange.start"] == str(_milliseconds("2025-10-23T00:00:00Z"))
        assert first_params["timeIntervals.timeRange.end"] == str(end_ms)

        frozen_time.move_to("2026-10-23T14:37:12Z")
        state = StateBuilder().with_stream_state(stream_name, first_output.most_recent_state.stream_state).build()
        second_output, second_endpoint = _read(stream_name, _CONFIG, {"elements": []}, state)

    # The cursor already equals today - 2 days at midnight: a shorter window would be rejected with 400.
    assert not second_output.errors
    assert second_endpoint.call_count == 0
    assert second_output.most_recent_state.stream_state == first_output.most_recent_state.stream_state


_MONTH_CONFIG = {**_CONFIG, "time_granularity_type": "MONTH"}


@pytest.mark.parametrize("stream_name", list(_STREAMS))
@freeze_time("2026-10-23T14:37:12Z")
def test_month_first_sync_requests_complete_months_only(stream_name):
    output, endpoint = _read(stream_name, _MONTH_CONFIG, {"elements": []})

    assert not output.errors
    assert endpoint.call_count == 1
    assert _query_params(endpoint.last_request) == _expected_query(
        stream_name,
        _milliseconds("2025-10-23T00:00:00Z"),
        _milliseconds("2026-10-01T00:00:00Z"),
        "MONTH",
    )


@pytest.mark.parametrize("stream_name", list(_STREAMS))
@freeze_time("2026-10-23T14:37:12Z")
def test_month_sync_inside_the_current_month_requests_nothing(stream_name):
    state = StateBuilder().with_stream_state(stream_name, {"timeRangeEnd": _milliseconds("2026-10-01T00:00:00Z")}).build()
    output, endpoint = _read(stream_name, _MONTH_CONFIG, {"elements": []}, state)

    assert not output.errors
    assert endpoint.call_count == 0


@pytest.mark.parametrize("stream_name", list(_STREAMS))
@freeze_time("2026-11-02T23:00:00Z")
def test_month_sync_waits_until_two_days_after_the_month_ends(stream_name):
    state = StateBuilder().with_stream_state(stream_name, {"timeRangeEnd": _milliseconds("2026-10-01T00:00:00Z")}).build()
    output, endpoint = _read(stream_name, _MONTH_CONFIG, {"elements": []}, state)

    assert not output.errors
    assert endpoint.call_count == 0


@pytest.mark.parametrize(
    "now",
    [
        "2026-11-03T00:00:00Z",
        "2026-11-10T05:00:00Z",
    ],
)
@pytest.mark.parametrize(
    "cursor",
    [
        "2026-10-01T00:00:00Z",
        # A state written before 1.2.0, when the MONTH window ended in the middle of a month.
        "2026-10-21T00:00:00Z",
    ],
)
@pytest.mark.parametrize("stream_name", list(_STREAMS))
def test_month_sync_after_the_month_closes_ends_on_the_month_boundary(stream_name, cursor, now):
    state = StateBuilder().with_stream_state(stream_name, {"timeRangeEnd": _milliseconds(cursor)}).build()
    with freeze_time(now):
        output, endpoint = _read(stream_name, _MONTH_CONFIG, {"elements": []}, state)

    assert not output.errors
    assert endpoint.call_count == 1
    assert _query_params(endpoint.last_request) == _expected_query(
        stream_name,
        _milliseconds(cursor),
        _milliseconds("2026-11-01T00:00:00Z"),
        "MONTH",
    )
