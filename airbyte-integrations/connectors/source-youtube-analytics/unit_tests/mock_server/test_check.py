#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""The connection check on a channel where YouTube no longer produces the annotations report.

`channel_annotations_a1` is absent from YouTube's current channel report list (it documents
`channel_annotations_a2`). A channel that still has an old job for it gets no report files,
and a channel without one cannot create it. Neither may stop the user from setting up the
source while the channel's supported reports are available.
"""

import logging
from typing import Any, Dict, List

import pytest
import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status


_API = YoutubeAnalyticsRequestBuilder.BASE_URL
_BASIC_JOB = {"id": "job-basic", "reportTypeId": "channel_basic_a3"}
_ANNOTATIONS_JOB = {"id": "job-annotations", "reportTypeId": "channel_annotations_a1"}
_BASIC_CSV = (
    "date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,views\n"
    "20261018,channel-1,video-1,on_demand,subscribed,US,7\n"
)


@pytest.mark.parametrize(
    "jobs",
    [
        pytest.param([_ANNOTATIONS_JOB, _BASIC_JOB], id="old-annotations-job-has-no-report-files"),
        pytest.param([_BASIC_JOB], id="annotations-job-cannot-be-created"),
    ],
)
def test_check_succeeds_when_the_annotations_report_is_unavailable(jobs: List[Dict[str, Any]]) -> None:
    config = ConfigBuilder().build()

    with requests_mock.Mocker() as mocker:
        mocker.post(YoutubeAnalyticsRequestBuilder.TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(f"{_API}/jobs", json={"jobs": jobs})
        # YouTube rejects creating a job for a report type it no longer supports.
        mocker.post(f"{_API}/jobs", status_code=400, json={"error": {"code": 400, "message": "Invalid report type."}})
        # A job for a report YouTube stopped generating lists no files.
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
        mocker.get(f"{_API}/media/CHANNEL/report-basic", text=_BASIC_CSV)

        status = get_source(config).check(logging.getLogger("test"), config)

        api_calls = [(request.method, request.path) for request in mocker.request_history if request.hostname != "oauth2.googleapis.com"]

    assert status.status == Status.SUCCEEDED, status.message
    # The check reads one supported report end to end, and neither lists nor tries to create
    # anything for the annotations report.
    assert api_calls == [
        ("GET", "/v1/jobs"),
        ("GET", "/v1/jobs/job-basic/reports"),
        ("GET", "/v1/media/channel/report-basic"),
    ]
