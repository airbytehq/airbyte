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


def test_check_succeeds_without_retired_annotations_report() -> None:
    config = ConfigBuilder().build()
    job = {"id": "basic-job", "reportTypeId": "channel_basic_a3"}
    jobs = HttpResponse(body=json.dumps({"jobs": [job]}))

    with HttpMocker() as http_mocker:
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            jobs,
        )
        create_annotations_job = HttpRequest(
            url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
            body={"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"},
        )
        http_mocker.post(
            create_annotations_job,
            HttpResponse(body=json.dumps({"error": {"code": 400, "message": "Report type is not available"}}), status_code=400),
        )
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        report_id = "basic-report"
        reports = [
            {
                "id": report_id,
                "jobId": job["id"],
                "startTime": "2026-11-10T00:00:00Z",
                "endTime": "2026-11-11T00:00:00Z",
                "createTime": "2026-11-11T01:00:00Z",
                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(report_id),
            }
        ]
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint(job["id"]).with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(body=json.dumps({"reports": reports})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint(report_id).build(),
            HttpResponse(body="date,channel_id,video_id,views\n20261110,channel-1,video-1,3\n"),
        )

        result = get_source(config).check(logging.getLogger("test"), config)
        http_mocker.assert_number_of_calls(create_annotations_job, 0)

    assert result.status == Status.SUCCEEDED, result.message
