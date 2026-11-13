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
_BASIC_JOB_ID = "job-basic"
_BASIC_REPORT_ID = "report-basic"
# A job created for `channel_annotations_a1` before YouTube retired the report type. It is
# still listed, but YouTube no longer generates report files for it.
_LEGACY_ANNOTATIONS_JOB = {"id": "job-annotations", "reportTypeId": "channel_annotations_a1"}


def test_check_succeeds_when_retired_annotations_report_has_no_files() -> None:
    config = ConfigBuilder().build()

    with requests_mock.Mocker() as mocker:
        mocker.post(YoutubeAnalyticsRequestBuilder.TOKEN_URL, json={"access_token": "token", "expires_in": 3600})
        mocker.get(
            f"{_API}/jobs",
            json={"jobs": [_LEGACY_ANNOTATIONS_JOB, {"id": _BASIC_JOB_ID, "reportTypeId": "channel_basic_a3"}]},
        )
        mocker.get(f"{_API}/jobs/{_LEGACY_ANNOTATIONS_JOB['id']}/reports", json={})
        mocker.get(
            f"{_API}/jobs/{_BASIC_JOB_ID}/reports",
            json={
                "reports": [
                    {
                        "id": _BASIC_REPORT_ID,
                        "jobId": _BASIC_JOB_ID,
                        "startTime": "2026-11-10T08:00:00Z",
                        "endTime": "2026-11-11T08:00:00Z",
                        "createTime": "2026-11-12T00:00:00Z",
                        "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(_BASIC_REPORT_ID),
                    }
                ]
            },
        )
        mocker.get(
            YoutubeAnalyticsRequestBuilder.download_url(_BASIC_REPORT_ID),
            text="date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,views\n"
            "20261110,channel-1,video-1,on_demand,subscribed,US,5\n",
        )

        status = get_source(config).check(logging.getLogger("test"), config)
        history = mocker.request_history

    assert status.status == Status.SUCCEEDED, status.message
    assert [request.method for request in history if request.path == "/v1/jobs"] == ["GET"]
    assert [request.path for request in history if request.path.endswith("/reports")] == [f"/v1/jobs/{_BASIC_JOB_ID}/reports"]
    assert any(request.path == f"/v1/media/channel/{_BASIC_REPORT_ID}" for request in history)
