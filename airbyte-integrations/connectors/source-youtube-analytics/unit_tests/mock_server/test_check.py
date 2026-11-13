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


def test_check_succeeds_without_creating_a_retired_report_job():
    config = ConfigBuilder().build()
    retired_job = HttpRequest(
        url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
        body=json.dumps({"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"}),
    )

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(body=json.dumps({"jobs": [{"id": "job-1", "reportTypeId": "channel_basic_a3"}]})),
        )
        http_mocker.post(
            retired_job,
            HttpResponse(
                status_code=400,
                body=json.dumps(
                    {"error": {"code": 400, "message": "Unsupported report type: channel_annotations_a1", "status": "INVALID_ARGUMENT"}}
                ),
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint("job-1").with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": "report-1",
                                "jobId": "job-1",
                                "startTime": "2026-11-09T00:00:00Z",
                                "endTime": "2026-11-10T00:00:00Z",
                                "createTime": "2026-11-11T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("report-1"),
                            }
                        ]
                    }
                )
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint("report-1").build(),
            HttpResponse(body="date,channel_id,views\n20261109,channel-1,3\n"),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.status == Status.SUCCEEDED, status.message
        http_mocker.assert_number_of_calls(retired_job, 0)
