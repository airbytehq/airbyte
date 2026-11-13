#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status


@pytest.mark.parametrize("content_owner_id", [None, "owner-1"])
def test_check_uses_supported_report_when_retired_annotations_has_no_reports(content_owner_id: Optional[str]) -> None:
    config_builder = ConfigBuilder()
    if content_owner_id:
        config_builder.with_content_owner_id(content_owner_id)
    config = config_builder.build()
    api = YoutubeAnalyticsRequestBuilder.BASE_URL
    download_url = YoutubeAnalyticsRequestBuilder.download_url("basic-report")
    owner_query = {"onBehalfOfContentOwner": [content_owner_id]} if content_owner_id else {}

    with requests_mock.Mocker() as mocker:
        mocker.post(
            YoutubeAnalyticsRequestBuilder.TOKEN_URL,
            json={"access_token": "token", "expires_in": 3600},
        )
        mocker.get(
            f"{api}/jobs",
            [
                {
                    "json": {
                        "jobs": [{"id": "retired-job", "reportTypeId": "channel_annotations_a1"}],
                        "nextPageToken": "page-2",
                    }
                },
                {"json": {"jobs": [{"id": "basic-job", "reportTypeId": "channel_basic_a3"}]}},
            ],
        )
        # Existing retired jobs can remain listed even though they no longer produce files.
        mocker.get(f"{api}/jobs/retired-job/reports", json={})
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
        mocker.get(download_url, text="date,channel_id,video_id,views\n")

        status = get_source(config).check(logging.getLogger("test"), config)
        history = mocker.request_history

    assert status.status == Status.SUCCEEDED, status.message
    assert [
        (request.method, urlparse(request.url).path, parse_qs(urlparse(request.url).query))
        for request in history
        if request.url.startswith(api)
    ] == [
        ("GET", "/v1/jobs", owner_query),
        ("GET", "/v1/jobs", {**owner_query, "pageToken": ["page-2"]}),
        ("GET", "/v1/jobs", {**owner_query, "pageToken": ["page-2"]}),
        ("GET", "/v1/jobs/basic-job/reports", {**owner_query, "createdAfter": ["1990-01-01T00:00:00.000000Z"]}),
        ("GET", "/v1/media/CHANNEL/basic-report", {**owner_query, "alt": ["media"]}),
    ]
