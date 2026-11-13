# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the connection check.

The check drives the real manifest against a mocked YouTube Reporting API. YouTube retired the
`channel_annotations_a1` report type, so a channel's old annotations job no longer gets report
files and no job can be created for it. The check must read a report type YouTube still
supports instead.
"""

import logging
import time

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import Status


_API = "https://youtubereporting.googleapis.com/v1"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_BASIC_JOB_ID = "job-basic"
_ANNOTATIONS_JOB_ID = "job-annotations"


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)


def _download_url(report_id: str) -> str:
    return f"{_API}/media/CHANNEL/{report_id}?alt=media"


def test_check_reads_a_supported_report_instead_of_retired_channel_annotations_a1(config):
    """A channel with a `channel_basic_a3` report and a retired annotations job passes the check."""
    with requests_mock.Mocker() as mocker:
        mocker.post(_TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(
            f"{_API}/jobs",
            json={
                "jobs": [
                    {"id": _ANNOTATIONS_JOB_ID, "reportTypeId": "channel_annotations_a1"},
                    {"id": _BASIC_JOB_ID, "reportTypeId": "channel_basic_a3"},
                ]
            },
        )
        create_job = mocker.post(
            f"{_API}/jobs",
            status_code=400,
            json={"error": {"code": 400, "message": "Request contains an invalid argument.", "status": "INVALID_ARGUMENT"}},
        )
        # YouTube no longer generates files for the retired annotations report.
        mocker.get(f"{_API}/jobs/{_ANNOTATIONS_JOB_ID}/reports", json={})
        mocker.get(
            f"{_API}/jobs/{_BASIC_JOB_ID}/reports",
            json={
                "reports": [
                    {
                        "id": "r1",
                        "jobId": _BASIC_JOB_ID,
                        "startTime": "2026-10-01T00:00:00Z",
                        "endTime": "2026-10-02T00:00:00Z",
                        "createTime": "2026-10-02T00:00:00Z",
                        "downloadUrl": _download_url("r1"),
                    }
                ]
            },
        )
        mocker.get(_download_url("r1"), text="date,channel_id,views\n20261001,channel-1,3\n")

        status = get_source(config).check(logging.getLogger("test"), config)
        requested_paths = [(request.method, request.path) for request in mocker.request_history if request.method in ("GET", "POST")]

    assert status.status == Status.SUCCEEDED, status.message
    assert not create_job.called
    assert ("GET", f"/v1/jobs/{_BASIC_JOB_ID}/reports") in requested_paths
    assert ("GET", f"/v1/jobs/{_ANNOTATIONS_JOB_ID}/reports") not in requested_paths
    assert ("GET", "/v1/media/channel/r1") in requested_paths
