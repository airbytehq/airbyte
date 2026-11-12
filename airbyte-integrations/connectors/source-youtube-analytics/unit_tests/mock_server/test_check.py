#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging

import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status


_API = YoutubeAnalyticsRequestBuilder.BASE_URL
_ANNOTATIONS_JOB_ID = "job-annotations"
_BASIC_JOB_ID = "job-basic"
_BASIC_REPORT_ID = "report-basic"


def test_check_succeeds_when_the_retired_annotations_report_has_no_files() -> None:
    """`channel_annotations_a1` was retired by YouTube, so its job never gets a report file again.

    `check` must not depend on that report: a channel whose `channel_basic_a3` job has a report
    has working credentials and data, and the check has to pass without listing the
    annotations job's reports.
    """
    config = ConfigBuilder().build()

    with requests_mock.Mocker() as mocker:
        mocker.post(YoutubeAnalyticsRequestBuilder.TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(
            f"{_API}/jobs",
            json={
                "jobs": [
                    {"id": _ANNOTATIONS_JOB_ID, "reportTypeId": "channel_annotations_a1"},
                    {"id": _BASIC_JOB_ID, "reportTypeId": "channel_basic_a3"},
                ]
            },
        )
        # The API returns {} rather than {"reports": []} when a job has no report files.
        annotations_reports = mocker.get(f"{_API}/jobs/{_ANNOTATIONS_JOB_ID}/reports", json={})
        basic_reports = mocker.get(
            f"{_API}/jobs/{_BASIC_JOB_ID}/reports",
            json={
                "reports": [
                    {
                        "id": _BASIC_REPORT_ID,
                        "jobId": _BASIC_JOB_ID,
                        "startTime": "2026-11-09T08:00:00Z",
                        "endTime": "2026-11-10T08:00:00Z",
                        "createTime": "2026-11-11T00:00:00Z",
                        "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(_BASIC_REPORT_ID),
                    }
                ]
            },
        )
        download = mocker.get(
            YoutubeAnalyticsRequestBuilder.download_url(_BASIC_REPORT_ID),
            text="date,channel_id,video_id,views\n20261109,channel-1,video-1,7\n",
        )
        create_job = mocker.post(f"{_API}/jobs", json={})

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED, status.message
    assert basic_reports.call_count == 1
    assert basic_reports.last_request.qs == {"createdafter": ["1990-01-01t00:00:00.000000z"]}
    assert download.call_count == 1
    assert annotations_reports.call_count == 0
    assert create_job.call_count == 0
