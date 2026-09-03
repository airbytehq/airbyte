#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlparse

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_REPORTING_API = "https://youtubereporting.googleapis.com/v1"
_DOWNLOAD_OLD = f"{_REPORTING_API}/media/CHANNEL/r_old?alt=media"
_DOWNLOAD_NEW = f"{_REPORTING_API}/media/CHANNEL/r_new?alt=media"


def _reports() -> dict:
    return {
        "reports": [
            {
                "id": "r_old",
                "startTime": "2025-06-01T07:00:00Z",
                "endTime": "2025-06-02T07:00:00Z",
                "createTime": "2025-06-03T00:00:00Z",
                "downloadUrl": _DOWNLOAD_OLD,
            },
            {
                "id": "r_new",
                "startTime": "2026-03-01T07:00:00Z",
                "endTime": "2026-03-02T07:00:00Z",
                "createTime": "2026-03-03T00:00:00Z",
                "downloadUrl": _DOWNLOAD_NEW,
            },
        ]
    }


def _mock_reporting_api(mocker: requests_mock.Mocker) -> None:
    mocker.post("https://oauth2.googleapis.com/token", json={"access_token": "test_access_token", "expires_in": 3600})
    mocker.get(f"{_REPORTING_API}/jobs", json={"jobs": [{"id": "job-1", "reportTypeId": "channel_basic_a3"}]})
    mocker.get(f"{_REPORTING_API}/jobs/job-1/reports", json=_reports())
    mocker.get(_DOWNLOAD_OLD, text="date,channel_id,views\n20250601,c,1\n")
    mocker.get(_DOWNLOAD_NEW, text="date,channel_id,views\n20260301,c,2\n")


def _read_channel_basic(config, state=None):
    source = get_source(config=config, state=state)
    catalog = CatalogBuilder().with_stream("channel_basic_a3", SyncMode.incremental).build()
    return source, catalog


def _field(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name, None)


def test_incremental_state_sends_start_time_and_skips_old_reports(config):
    state = (
        StateBuilder()
        .with_stream_state(
            "channel_basic_a3",
            {
                "state": {"date": "20251107"},
                "parent_state": {
                    "report": {
                        "state": {"date": "2025-11-07T00:00:00.000000Z"},
                        "lookback_window": 0,
                    }
                },
            },
        )
        .build()
    )
    source, catalog = _read_channel_basic(config, state)

    with requests_mock.Mocker() as mocker:
        _mock_reporting_api(mocker)
        output = read(source, config, catalog)

    reports_request = next(request for request in mocker.request_history if request.path == "/v1/jobs/job-1/reports")
    query = parse_qs(urlparse(reports_request.url).query)
    assert query["startTimeAtOrAfter"] == ["2025-11-07T00:00:00.000000Z"]
    assert _DOWNLOAD_NEW in [request.url for request in mocker.request_history]
    assert _DOWNLOAD_OLD not in [request.url for request in mocker.request_history]
    assert len(output.records) == 1
    assert output.records[0].record.data["date"] == 20260301
    most_recent_state = output.most_recent_state
    assert most_recent_state is not None
    report_state = _field(_field(most_recent_state.stream_state, "parent_state"), "report")
    cursor_dates = []
    state_cursor = _field(report_state, "state")
    if state_cursor is not None:
        cursor_dates.append(_field(state_cursor, "date"))
    for partition_state in _field(report_state, "states") or []:
        cursor_dates.append(_field(_field(partition_state, "cursor"), "date"))
    assert "2026-03-01T07:00:00.000000Z" in cursor_dates


def test_initial_sync_requests_all_reports(config):
    source, catalog = _read_channel_basic(config)

    with requests_mock.Mocker() as mocker:
        _mock_reporting_api(mocker)
        output = read(source, config, catalog)

    reports_request = next(request for request in mocker.request_history if request.path == "/v1/jobs/job-1/reports")
    query = parse_qs(urlparse(reports_request.url).query)
    assert not query.get("startTimeAtOrAfter")
    requested_urls = [request.url for request in mocker.request_history]
    assert _DOWNLOAD_OLD in requested_urls
    assert _DOWNLOAD_NEW in requested_urls
    assert len(output.records) == 2
