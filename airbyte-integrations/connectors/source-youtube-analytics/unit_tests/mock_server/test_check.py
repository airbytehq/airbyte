#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging

import freezegun
import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("has_rows", [False, True], ids=["header-only", "available-report"])
@freezegun.freeze_time("2026-11-11T00:00:00Z")
def test_check_succeeds_without_retired_annotations_job(has_rows: bool) -> None:
    config = ConfigBuilder().build()
    report_id = "report-basic"
    reports = [
        {
            "id": report_id,
            "jobId": "job-basic",
            "startTime": "2026-11-08T00:00:00Z",
            "endTime": "2026-11-09T00:00:00Z",
            "createTime": "2026-11-10T00:00:00Z",
            "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(report_id),
        }
    ]

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
            HttpResponse(
                body=json.dumps(
                    {"error": {"code": 400, "message": "Report type channel_annotations_a1 is not supported", "status": "INVALID_ARGUMENT"}}
                ),
                status_code=400,
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint("job-basic").with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(body=json.dumps({"reports": reports})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint(report_id).build(),
            HttpResponse(body="date,channel_id,views\n" + ("20261108,channel-1,3\n" if has_rows else "")),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED, status.message
