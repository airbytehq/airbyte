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
_DOWNLOAD_SAME = f"{_REPORTING_API}/media/CHANNEL/r_same?alt=media"
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
                "id": "r_same",
                "startTime": "2025-11-07T07:00:00Z",
                "endTime": "2025-11-08T07:00:00Z",
                "createTime": "2025-11-09T00:00:00Z",
                "downloadUrl": _DOWNLOAD_SAME,
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
    mocker.get(_DOWNLOAD_SAME, text="date,channel_id,views\n20251107,c,2\n")
    mocker.get(_DOWNLOAD_NEW, text="date,channel_id,views\n20260301,c,3\n")


def _read_channel_basic(config, state=None):
    source = get_source(config=config, state=state)
    catalog = CatalogBuilder().with_stream("channel_basic_a3", SyncMode.incremental).build()
    return source, catalog


def _reports_request(mocker: requests_mock.Mocker):
    return next(request for request in mocker.request_history if request.path == "/v1/jobs/job-1/reports")


def _downloaded_urls(mocker: requests_mock.Mocker) -> list[str]:
    return [request.url for request in mocker.request_history]


def test_migrated_low_code_state_filters_reports(config):
    state = (
        StateBuilder()
        .with_stream_state(
            "channel_basic_a3",
            {
                "state": {"date": "20251107"},
                "parent_state": {
                    "report": {
                        "state": {"date": "2025-11-07T07:00:00.000000Z"},
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

    query = parse_qs(urlparse(_reports_request(mocker).url).query, keep_blank_values=True)
    assert query == {"startTimeAtOrAfter": ["2025-11-07T07:00:00.000000Z"]}
    requested_urls = _downloaded_urls(mocker)
    assert _DOWNLOAD_OLD not in requested_urls
    assert _DOWNLOAD_SAME not in requested_urls
    assert _DOWNLOAD_NEW in requested_urls
    assert len(output.records) == 1
    assert output.records[0].record.data["date"] == 20260301
    report_state = output.most_recent_state.stream_state.__dict__["parent_state"]["report"]
    assert report_state["state"] == {"date": "2026-03-01T07:00:00.000000Z"}
    assert [state["cursor"] for state in report_state["states"]] == [{"date": "2026-03-01T07:00:00.000000Z"}]


def test_legacy_state_migrates_and_filters_reports(config):
    state = StateBuilder().with_stream_state("channel_basic_a3", {"date": 20251107}).build()
    source, catalog = _read_channel_basic(config, state)

    with requests_mock.Mocker() as mocker:
        _mock_reporting_api(mocker)
        output = read(source, config, catalog)

    query = parse_qs(urlparse(_reports_request(mocker).url).query)
    assert query == {"startTimeAtOrAfter": ["2025-11-07T00:00:00.000000Z"]}
    requested_urls = _downloaded_urls(mocker)
    assert _DOWNLOAD_OLD not in requested_urls
    assert _DOWNLOAD_SAME in requested_urls
    assert _DOWNLOAD_NEW in requested_urls
    assert len(output.records) == 2


def test_initial_sync_requests_all_reports(config):
    source, catalog = _read_channel_basic(config)

    with requests_mock.Mocker() as mocker:
        _mock_reporting_api(mocker)
        output = read(source, config, catalog)

    query = parse_qs(urlparse(_reports_request(mocker).url).query, keep_blank_values=True)
    assert query == {"startTimeAtOrAfter": ["1990-01-01T00:00:00.000000Z"]}
    requested_urls = _downloaded_urls(mocker)
    assert _DOWNLOAD_OLD in requested_urls
    assert _DOWNLOAD_SAME in requested_urls
    assert _DOWNLOAD_NEW in requested_urls
    assert len(output.records) == 3
