#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging

import freezegun
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@freezegun.freeze_time("2026-10-21T00:00:00Z")
def test_check_succeeds_without_retired_annotations_job() -> None:
    config = ConfigBuilder().build()
    token_request = YoutubeAnalyticsRequestBuilder.token_request()
    jobs_request = YoutubeAnalyticsRequestBuilder.jobs_endpoint().build()
    retired_job_request = HttpRequest(
        url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
        body=json.dumps({"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"}),
    )
    reports_request = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint("job-basic")
        .with_created_after("1990-01-01T00:00:00.000000Z")
        .build()
    )
    download_request = YoutubeAnalyticsRequestBuilder.download_endpoint("report-basic").build()

    with HttpMocker() as http_mocker:
        http_mocker.post(token_request, HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})))
        http_mocker.get(
            jobs_request,
            HttpResponse(body=json.dumps({"jobs": [{"id": "job-basic", "reportTypeId": "channel_basic_a3"}]})),
        )
        http_mocker.post(
            retired_job_request,
            HttpResponse(
                status_code=400,
                body=json.dumps({"error": {"code": 400, "status": "INVALID_ARGUMENT", "message": "Unsupported report type"}}),
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
        http_mocker.get(download_request, HttpResponse(body="date,channel_id,views\n20261018,channel-1,3\n"))

        result = get_source(config=config).check(logging.getLogger("test"), config)

        assert result.status == Status.SUCCEEDED, result.message
        http_mocker.assert_number_of_calls(token_request, 3)
        http_mocker.assert_number_of_calls(jobs_request, 1)
        http_mocker.assert_number_of_calls(retired_job_request, 0)
        http_mocker.assert_number_of_calls(reports_request, 1)
        http_mocker.assert_number_of_calls(download_request, 1)
