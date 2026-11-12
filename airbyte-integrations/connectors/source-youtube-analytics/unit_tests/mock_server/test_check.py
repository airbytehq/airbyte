#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional
from urllib.parse import parse_qs, urlencode, urlparse

import pytest
import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status


_API = YoutubeAnalyticsRequestBuilder.BASE_URL


@pytest.mark.parametrize("content_owner_id", [None, "owner-1"])
def test_check_downloads_supported_report_without_creating_deprecated_job(content_owner_id: Optional[str]) -> None:
    builder = ConfigBuilder()
    if content_owner_id:
        builder.with_content_owner_id(content_owner_id)
    config = builder.build()
    owner_params = {"onBehalfOfContentOwner": content_owner_id} if content_owner_id else {}

    with requests_mock.Mocker() as mocker:
        mocker.post(
            YoutubeAnalyticsRequestBuilder.TOKEN_URL,
            json={"access_token": "token", "expires_in": 3600},
        )
        jobs = mocker.get(
            f"{_API}/jobs?{urlencode(owner_params)}",
            json={"jobs": [{"id": "basic-job", "reportTypeId": "channel_basic_a3"}]},
            complete_qs=True,
        )
        # The retired report never appears in jobs.list, even after a creation attempt.
        create_job = mocker.post(f"{_API}/jobs", json={"id": "retired-job"})
        reports = mocker.get(
            f"{_API}/jobs/basic-job/reports",
            json={
                "reports": [
                    {
                        "id": "report-1",
                        "jobId": "basic-job",
                        "createTime": "2026-10-01T00:00:00Z",
                        "startTime": "2026-10-01T00:00:00Z",
                        "endTime": "2026-10-02T00:00:00Z",
                        "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("report-1"),
                    }
                ]
            },
        )
        download = mocker.get(
            YoutubeAnalyticsRequestBuilder.download_url("report-1"),
            text="date,channel_id,video_id,views\n20261001,channel-1,video-1,3\n",
        )

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED, status.message
    assert jobs.call_count == 1
    assert not create_job.called
    assert reports.call_count == 1
    assert parse_qs(urlparse(reports.last_request.url).query) == {
        "createdAfter": ["1990-01-01T00:00:00.000000Z"],
        **{key: [value] for key, value in owner_params.items()},
    }
    assert download.call_count == 1
    assert parse_qs(urlparse(download.last_request.url).query) == {
        "alt": ["media"],
        **{key: [value] for key, value in owner_params.items()},
    }
