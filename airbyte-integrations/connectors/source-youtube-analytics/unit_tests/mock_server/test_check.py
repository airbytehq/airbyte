#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Connection check against a channel whose retired report types no longer produce reports.

YouTube retired `channel_annotations_a1` (the Reporting API now lists `channel_annotations_a2`),
so a job for it lists no report files and the connection check must not depend on it.
https://developers.google.com/youtube/reporting/v1/reports/channel_reports
"""

import logging

import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status


_API = YoutubeAnalyticsRequestBuilder.BASE_URL


def test_check_succeeds_when_the_retired_annotations_report_lists_no_files() -> None:
    config = ConfigBuilder().build()

    with requests_mock.Mocker() as mocker:
        mocker.post(YoutubeAnalyticsRequestBuilder.TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(
            f"{_API}/jobs",
            json={
                "jobs": [
                    {"id": "job-annotations", "reportTypeId": "channel_annotations_a1"},
                    {"id": "job-basic", "reportTypeId": "channel_basic_a3"},
                ]
            },
        )
        create_job = mocker.post(f"{_API}/jobs", json={"id": "unexpected"})
        mocker.get(f"{_API}/jobs/job-annotations/reports", json={})
        mocker.get(
            f"{_API}/jobs/job-basic/reports",
            json={
                "reports": [
                    {
                        "id": "report-basic",
                        "jobId": "job-basic",
                        "startTime": "2026-10-18T07:00:00Z",
                        "endTime": "2026-10-19T07:00:00Z",
                        "createTime": "2026-10-20T00:00:00Z",
                        "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("report-basic"),
                    }
                ]
            },
        )
        mocker.get(
            YoutubeAnalyticsRequestBuilder.download_url("report-basic"),
            text="date,channel_id,video_id,views\n20261018,channel-1,video-1,3\n",
        )

        status = get_source(config).check(logging.getLogger("test"), config)
        listed_report_paths = [request.path for request in mocker.request_history if request.path.endswith("/reports")]

    assert status.status == Status.SUCCEEDED, status.message
    assert listed_report_paths == ["/v1/jobs/job-basic/reports"]
    assert not create_job.called
