#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging

import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("row_count", [0, 1], ids=["header-only", "one-row"])
def test_check_succeeds_without_retired_reporting_jobs(row_count: int) -> None:
    config = ConfigBuilder().build()

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(body=json.dumps({"jobs": [{"id": "job-basic", "reportTypeId": "channel_basic_a3"}]})),
        )
        http_mocker.post(
            HttpRequest(
                url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
                body=json.dumps({"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"}),
            ),
            HttpResponse(status_code=400, body=json.dumps({"error": {"code": 400, "message": "Invalid report type"}})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint("job-basic").with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(
                body=json.dumps(
                    {
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
                    }
                )
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint("report-basic").build(),
            HttpResponse(body="date,channel_id,video_id,views\n" + "20261018,channel-1,video-1,1\n" * row_count),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED, status.message
