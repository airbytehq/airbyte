#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging

from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def test_check_succeeds_when_only_supported_basic_report_job_exists() -> None:
    config = ConfigBuilder().build()
    job_id = "job-channel-basic"
    report_id = "report-channel-basic"

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(body=json.dumps({"jobs": [{"id": job_id, "reportTypeId": "channel_basic_a3"}]})),
        )
        http_mocker.post(
            HttpRequest(
                url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
                body=json.dumps({"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"}),
            ),
            HttpResponse(
                status_code=400,
                body=json.dumps({"error": {"code": 400, "status": "INVALID_ARGUMENT", "message": "Report type is retired"}}),
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint(job_id).with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": report_id,
                                "jobId": job_id,
                                "startTime": "2026-11-03T07:00:00Z",
                                "endTime": "2026-11-04T07:00:00Z",
                                "createTime": "2026-11-05T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(report_id),
                            }
                        ]
                    }
                )
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint(report_id).build(),
            HttpResponse(body="date,channel_id,video_id,views\n20261103,channel-1,video-1,3\n"),
        )
        result = get_source(config).check(logging.getLogger(__name__), config)

    assert result.status == Status.SUCCEEDED, result.message
