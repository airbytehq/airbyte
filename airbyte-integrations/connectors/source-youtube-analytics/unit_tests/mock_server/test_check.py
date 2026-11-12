#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""`check` must probe a report type YouTube still generates.

YouTube retired `channel_annotations_a1`: a job for it no longer produces report files, so a
`check` that probes that report finds no report to read and fails with "no stream slices were
found" on every account, blocking source setup.
"""

import logging
import time

import pytest
import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status


_API = YoutubeAnalyticsRequestBuilder.BASE_URL
_ANNOTATIONS_JOB = {"id": "job-annotations", "reportTypeId": "channel_annotations_a1"}
_BASIC_JOB = {"id": "job-basic", "reportTypeId": "channel_basic_a3"}
_REPORT_ID = "report-basic-1"


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)


def _register_token(mocker: requests_mock.Mocker) -> None:
    mocker.post(YoutubeAnalyticsRequestBuilder.TOKEN_URL, json={"access_token": "token", "expires_in": 3600})


def _register_reports(mocker: requests_mock.Mocker) -> requests_mock.adapter._Matcher:
    # The retired report type's job still exists but YouTube no longer generates files for it.
    mocker.get(f"{_API}/jobs/{_ANNOTATIONS_JOB['id']}/reports", json={})
    mocker.get(
        f"{_API}/jobs/{_BASIC_JOB['id']}/reports",
        json={
            "reports": [
                {
                    "id": _REPORT_ID,
                    "jobId": _BASIC_JOB["id"],
                    "startTime": "2026-11-09T08:00:00Z",
                    "endTime": "2026-11-10T08:00:00Z",
                    "createTime": "2026-11-11T00:00:00Z",
                    "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(_REPORT_ID),
                }
            ]
        },
    )
    return mocker.get(
        YoutubeAnalyticsRequestBuilder.download_url(_REPORT_ID),
        text="date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,views\n"
        "20261109,channel-1,video-1,on_demand,subscribed,US,10\n",
    )


def test_check_succeeds_when_the_retired_annotations_report_has_no_files():
    config = ConfigBuilder().build()
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        jobs = mocker.get(f"{_API}/jobs", json={"jobs": [_ANNOTATIONS_JOB, _BASIC_JOB]})
        download = _register_reports(mocker)

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED, status.message
    assert download.call_count == 1
    # Both job types already exist, so check must not create a job.
    assert [request.method for request in jobs.request_history] == ["GET"]


def test_check_creates_a_job_only_for_a_supported_report_type():
    """On an account with no jobs, `check` creates its probe job for `channel_basic_a3`, never the retired report."""
    config = ConfigBuilder().build()
    with requests_mock.Mocker() as mocker:
        _register_token(mocker)
        created = []

        def list_jobs(request, context):
            return {"jobs": created}

        def create_job(request, context):
            body = request.json()
            job = {"id": f"job-{body['reportTypeId']}", "reportTypeId": body["reportTypeId"]}
            created.append(job)
            return job

        jobs_get = mocker.get(f"{_API}/jobs", json=list_jobs)
        jobs_post = mocker.post(f"{_API}/jobs", json=create_job)
        mocker.get(f"{_API}/jobs/job-channel_basic_a3/reports", json={})
        mocker.get(f"{_API}/jobs/job-channel_annotations_a1/reports", json={})

        get_source(config).check(logging.getLogger("test"), config)

    assert jobs_get.called
    assert [request.json() for request in jobs_post.request_history] == [
        {"name": "Airbyte reporting job", "reportTypeId": "channel_basic_a3"}
    ]
