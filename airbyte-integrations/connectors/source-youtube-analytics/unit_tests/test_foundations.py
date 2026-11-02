# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for listing pagination, report value types, and error handling.

Every test drives the real manifest against a mocked YouTube Reporting API, and asserts the
outgoing requests as well as the output, so a filter or paginator removed from the manifest
fails the test rather than passing silently.
"""

import logging
import time
from typing import Any, Dict, List, Optional

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_API = "https://youtubereporting.googleapis.com/v1"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_STREAM = "channel_basic_a3"
_JOB_ID = "job-1"

# Streams with no rows for the CI test channel; must match `empty_streams` in
# acceptance-test-config.yml.
_EMPTY_STREAMS = [
    "channel_annotations_a1",
    "channel_cards_a1",
    "channel_demographics_a1",
    "channel_end_screens_a1",
    "channel_province_a3",
    "channel_sharing_service_a1",
    "playlist_basic_a2",
    "playlist_combined_a2",
    "playlist_device_os_a2",
    "playlist_playback_location_a2",
    "playlist_province_a2",
    "playlist_traffic_source_a2",
]


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)


def _download_url(report_id: str) -> str:
    return f"{_API}/media/CHANNEL/{report_id}?alt=media"


def _listing(report_id: str, create_time: str) -> Dict[str, Any]:
    return {
        "id": report_id,
        "jobId": _JOB_ID,
        "startTime": create_time,
        "endTime": create_time,
        "createTime": create_time,
        "downloadUrl": _download_url(report_id),
    }


def _paged(pages: Dict[Optional[str], Dict[str, Any]]):
    """A requests_mock callback serving one body per `pageToken` value (None = first page)."""

    def callback(request, context):
        token = request.qs.get("pagetoken", [None])[0]
        if token not in pages:
            context.status_code = 400
            return {"error": {"code": 400, "message": f"unexpected pageToken {token}"}}
        return pages[token]

    return callback


def _register_token(mocker: requests_mock.Mocker) -> None:
    mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})


def _register_job(mocker: requests_mock.Mocker, stream: str = _STREAM) -> None:
    mocker.get(f"{_API}/jobs", json={"jobs": [{"id": _JOB_ID, "reportTypeId": stream}]})


def _read(config, stream: str = _STREAM):
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog)


def _page_tokens(history, path: str) -> List[Optional[str]]:
    return [request.qs.get("pagetoken", [None])[0] for request in history if request.method == "GET" and request.path == path]


def test_jobs_listing_follows_next_page_token_and_does_not_create_a_duplicate_job(config):
    """The stream's job is on page 2 of `jobs.list`: it must be found, not re-created."""
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        mocker.get(
            f"{_API}/jobs",
            json=_paged(
                {
                    None: {"jobs": [{"id": "other-job", "reportTypeId": "channel_cards_a1"}], "nextPageToken": "jobs-page-2"},
                    "jobs-page-2": {"jobs": [{"id": _JOB_ID, "reportTypeId": _STREAM}]},
                }
            ),
        )
        create_job = mocker.post(f"{_API}/jobs", json={"id": "duplicate"})
        mocker.get(f"{_API}/jobs/{_JOB_ID}/reports", json={"reports": [_listing("r1", "2026-10-01T00:00:00Z")]})
        mocker.get(_download_url("r1"), text="date,channel_id,views\n20261001,channel-1,3\n")

        output = _read(config)
        history = mocker.request_history

    assert output.errors == []
    assert not create_job.called
    assert [record.record.data["views"] for record in output.records] == [3]
    assert "jobs-page-2" in _page_tokens(history, "/v1/jobs")


def test_job_is_created_only_when_absent_from_every_page(config):
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        listings = iter(
            [
                {"jobs": [{"id": "other-job", "reportTypeId": "channel_cards_a1"}], "nextPageToken": "jobs-page-2"},
                {"jobs": [{"id": "another-job", "reportTypeId": "channel_combined_a3"}]},
                {"jobs": [{"id": _JOB_ID, "reportTypeId": _STREAM}]},
            ]
        )
        mocker.get(f"{_API}/jobs", json=lambda request, context: next(listings))
        create_job = mocker.post(f"{_API}/jobs", json={"id": _JOB_ID})
        mocker.get(f"{_API}/jobs/{_JOB_ID}/reports", json={})

        output = _read(config)
        tokens = _page_tokens(mocker.request_history, "/v1/jobs")

    assert output.errors == []
    assert create_job.call_count == 1
    assert create_job.last_request.json() == {"name": "Airbyte reporting job", "reportTypeId": _STREAM}
    assert tokens == [None, "jobs-page-2", None]


def test_reports_listing_follows_next_page_token(config):
    """Report files on page 2 of `jobs.reports.list` are downloaded too."""
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        _register_job(mocker)
        mocker.get(
            f"{_API}/jobs/{_JOB_ID}/reports",
            json=_paged(
                {
                    None: {"reports": [_listing("r1", "2026-10-01T00:00:00Z")], "nextPageToken": "reports-page-2"},
                    "reports-page-2": {"reports": [_listing("r2", "2026-10-02T00:00:00Z")]},
                }
            ),
        )
        mocker.get(_download_url("r1"), text="date,channel_id,views\n20261001,channel-1,1\n")
        mocker.get(_download_url("r2"), text="date,channel_id,views\n20261002,channel-1,2\n")

        output = _read(config)
        history = mocker.request_history

    assert output.errors == []
    assert sorted(record.record.data["date"] for record in output.records) == [20261001, 20261002]
    report_requests = [request for request in history if request.path == f"/v1/jobs/{_JOB_ID}/reports"]
    assert [request.qs.get("pagetoken", [None])[0] for request in report_requests] == [None, "reports-page-2"]
    # The cursor filter is sent on every page, not just the first.
    assert all(request.qs["createdafter"] == ["1990-01-01t00:00:00.000000z"] for request in report_requests)


def test_report_values_are_emitted_as_their_declared_types(config):
    """CSV text is cast to the schema's integer/number types; strings stay strings."""
    csv = (
        "date,channel_id,video_id,views,engaged_views,subscribers_lost,red_views,watch_time_minutes,"
        "average_view_duration_percentage,annotation_click_through_rate,country_code\n"
        "20261016,channel-1,video-1,2,2,0,5,0.14745,1.9149350649350649,0,UA\n"
    )
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        _register_job(mocker)
        mocker.get(f"{_API}/jobs/{_JOB_ID}/reports", json={"reports": [_listing("r1", "2026-10-18T00:00:00Z")]})
        mocker.get(_download_url("r1"), text=csv)

        output = _read(config)

    assert output.errors == []
    record = output.records[0].record.data
    assert record == {
        "date": 20261016,
        "channel_id": "channel-1",
        "video_id": "video-1",
        "views": 2,
        "engaged_views": 2,
        "subscribers_lost": 0,
        "red_views": 5,
        "watch_time_minutes": 0.14745,
        "average_view_duration_percentage": 1.9149350649350649,
        "annotation_click_through_rate": 0.0,
        "country_code": "UA",
    }
    assert isinstance(record["views"], int)
    assert isinstance(record["annotation_click_through_rate"], float)


def test_report_value_that_does_not_parse_is_left_unchanged(config):
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        _register_job(mocker)
        mocker.get(f"{_API}/jobs/{_JOB_ID}/reports", json={"reports": [_listing("r1", "2026-10-18T00:00:00Z")]})
        mocker.get(_download_url("r1"), text="date,channel_id,views\n20261016,channel-1,\n")

        output = _read(config)

    assert output.errors == []
    assert output.records[0].record.data["views"] == ""


def test_404_on_report_download_skips_the_file_and_keeps_syncing(config):
    """An expired or removed report file must not fail the whole sync."""
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        _register_job(mocker)
        mocker.get(
            f"{_API}/jobs/{_JOB_ID}/reports",
            json={"reports": [_listing("gone", "2026-10-01T00:00:00Z"), _listing("r2", "2026-10-02T00:00:00Z")]},
        )
        gone = mocker.get(
            _download_url("gone"),
            status_code=404,
            json={"error": {"code": 404, "message": "Requested entity was not found.", "status": "NOT_FOUND"}},
        )
        mocker.get(_download_url("r2"), text="date,channel_id,views\n20261002,channel-1,2\n")

        output = _read(config)

    assert output.errors == []
    assert gone.call_count == 1
    assert [record.record.data["date"] for record in output.records] == [20261002]


def test_404_on_a_listing_endpoint_still_fails(config):
    """The 404 IGNORE filter is scoped to downloads; a missing job is a real error."""
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        _register_job(mocker)
        mocker.get(
            f"{_API}/jobs/{_JOB_ID}/reports",
            status_code=404,
            json={"error": {"code": 404, "message": "Requested entity was not found.", "status": "NOT_FOUND"}},
        )

        output = _read(config)

    assert output.errors
    assert output.records == []


def test_403_fails_as_config_error_quoting_the_vendor_message(config):
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        mocker.get(
            f"{_API}/reportTypes",
            status_code=403,
            json={"error": {"code": 403, "message": "The caller does not have permission", "status": "PERMISSION_DENIED"}},
        )

        output = _read(config, stream="report_types")

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "The YouTube Reporting API denied access: The caller does not have permission." in error.message


def test_403_without_a_json_body_still_has_a_message(config):
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        mocker.get(f"{_API}/reportTypes", status_code=403, text="Forbidden")

        output = _read(config, stream="report_types")

    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "denied access: see the YouTube Reporting API error." in error.message


def test_expired_refresh_token_tells_the_user_to_re_authenticate(config):
    with requests_mock.Mocker() as mocker:
        mocker.post(
            _TOKEN_URL,
            status_code=400,
            json={"error": "invalid_grant", "error_description": "Token has been expired or revoked."},
        )

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.FAILED
    assert "Refresh token is invalid or expired" in status.message


@pytest.mark.parametrize("stream", _EMPTY_STREAMS)
def test_empty_stream_with_header_only_report_reads_cleanly(config, stream):
    """These streams have no rows for the CI channel; a header-only report file yields no records and no error."""
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        _register_job(mocker, stream=stream)
        mocker.get(f"{_API}/jobs/{_JOB_ID}/reports", json={"reports": [_listing("r1", "2026-10-18T00:00:00Z")]})
        download = mocker.get(_download_url("r1"), text="date,channel_id,video_id\n")

        output = _read(config, stream=stream)

    assert output.errors == []
    assert output.records == []
    assert download.called


def test_spec_declares_google_oauth_and_optional_num_workers(config):
    spec = get_source(config).spec(logging.getLogger("test"))
    properties = spec.connectionSpecification["properties"]

    assert properties["credentials"]["order"] == 1
    assert properties["num_workers"]["minimum"] == 1
    assert properties["num_workers"]["maximum"] == 4
    assert "num_workers" not in spec.connectionSpecification["required"]

    oauth = spec.advanced_auth.oauth_config_specification
    connector_input = oauth.oauth_connector_input_specification
    assert connector_input.consent_url.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "access_type=offline" in connector_input.consent_url
    assert "prompt=consent" in connector_input.consent_url
    assert connector_input.access_token_url.startswith("https://oauth2.googleapis.com/token?")
    assert connector_input.extract_output == ["refresh_token"]
    assert [scope["scope"] for scope in connector_input.scopes] == [
        "https://www.googleapis.com/auth/yt-analytics.readonly",
        "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
    ]
    # Config paths are unchanged, so existing connections keep working.
    assert oauth.complete_oauth_output_specification["properties"]["refresh_token"]["path_in_connector_config"] == [
        "credentials",
        "refresh_token",
    ]
    assert oauth.complete_oauth_server_output_specification["properties"]["client_id"]["path_in_connector_config"] == [
        "credentials",
        "client_id",
    ]
