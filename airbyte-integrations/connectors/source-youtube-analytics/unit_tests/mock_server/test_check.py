#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging

import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status


def test_check_uses_supported_report_when_retired_annotations_have_no_files():
    config = ConfigBuilder().build()
    api = YoutubeAnalyticsRequestBuilder.BASE_URL
    download_url = YoutubeAnalyticsRequestBuilder.download_url("basic-report")

    with requests_mock.Mocker(case_sensitive=True) as mocker:
        mocker.post(
            YoutubeAnalyticsRequestBuilder.TOKEN_URL,
            json={"access_token": "token", "expires_in": 3600},
        )
        mocker.get(
            f"{api}/jobs",
            json={
                "jobs": [
                    {"id": "annotations-job", "reportTypeId": "channel_annotations_a1"},
                    {"id": "basic-job", "reportTypeId": "channel_basic_a3"},
                ]
            },
        )
        mocker.get(f"{api}/jobs/annotations-job/reports", json={})
        mocker.get(
            f"{api}/jobs/basic-job/reports",
            json={
                "reports": [
                    {
                        "id": "basic-report",
                        "jobId": "basic-job",
                        "startTime": "2026-10-18T00:00:00Z",
                        "endTime": "2026-10-19T00:00:00Z",
                        "createTime": "2026-10-20T00:00:00Z",
                        "downloadUrl": download_url,
                    }
                ]
            },
        )
        mocker.get(download_url, text="date,channel_id,views\n20261018,channel-1,3\n")

        result = get_source(config).check(logging.getLogger("test"), config)
        history = [request for request in mocker.request_history if request.hostname == "youtubereporting.googleapis.com"]

    assert result.status == Status.SUCCEEDED, result.message
    assert [(request.method, request.path, request.qs) for request in history] == [
        ("GET", "/v1/jobs", {}),
        ("GET", "/v1/jobs/basic-job/reports", {"createdAfter": ["1990-01-01T00:00:00.000000Z"]}),
        ("GET", "/v1/media/CHANNEL/basic-report", {"alt": ["media"]}),
    ]
