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


def test_check_uses_supported_report_when_annotations_report_is_retired() -> None:
    config = ConfigBuilder().build()
    job_id = "job-channel_basic_a3"
    reports_request = YoutubeAnalyticsRequestBuilder.reports_endpoint(job_id).with_created_after("1990-01-01T00:00:00.000000Z").build()
    retired_job_request = HttpRequest(
        url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
        body={"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"},
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(body=json.dumps({"jobs": [{"id": job_id, "reportTypeId": "channel_basic_a3"}]})),
        )
        http_mocker.post(
            retired_job_request,
            HttpResponse(
                status_code=400,
                body=json.dumps(
                    {"error": {"code": 400, "message": "Report type channel_annotations_a1 is retired", "status": "INVALID_ARGUMENT"}}
                ),
            ),
        )
        http_mocker.get(
            reports_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": "report-basic",
                                "jobId": job_id,
                                "startTime": "2026-11-09T07:00:00Z",
                                "endTime": "2026-11-10T07:00:00Z",
                                "createTime": "2026-11-11T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("report-basic"),
                            }
                        ]
                    }
                )
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint("report-basic").build(),
            HttpResponse(body="date,channel_id,video_id,views\n20261109,channel-1,video-1,10\n"),
        )
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.status == Status.SUCCEEDED, status.message
        http_mocker.assert_number_of_calls(reports_request, 1)
        http_mocker.assert_number_of_calls(retired_job_request, 0)
