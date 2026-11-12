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


@pytest.mark.parametrize("job_exists", [True, False], ids=["existing-job", "create-job"])
@pytest.mark.parametrize("report_state", ["available", "empty", "forbidden"])
@freezegun.freeze_time("2026-11-12T00:00:00Z")
def test_check_uses_supported_channel_report(job_exists: bool, report_state: str) -> None:
    config = ConfigBuilder().build()
    jobs_request = YoutubeAnalyticsRequestBuilder.jobs_endpoint().build()
    jobs_response = HttpResponse(body=json.dumps({"jobs": [{"id": "basic-job", "reportTypeId": "channel_basic_a3"}]}))
    create_request = HttpRequest(
        url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
        body=json.dumps({"name": "Airbyte reporting job", "reportTypeId": "channel_basic_a3"}),
    )
    retired_create_request = HttpRequest(
        url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
        body=json.dumps({"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"}),
    )
    reports_request = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint("basic-job")
        .with_created_after("1990-01-01T00:00:00.000000Z")
        .build()
    )
    download_request = YoutubeAnalyticsRequestBuilder.download_endpoint("basic-report").build()
    reports = [
        {
            "id": "basic-report",
            "jobId": "basic-job",
            "startTime": "2026-11-09T07:00:00Z",
            "endTime": "2026-11-10T07:00:00Z",
            "createTime": "2026-11-11T00:00:00Z",
            "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("basic-report"),
        }
    ]
    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(jobs_request, jobs_response if job_exists else [HttpResponse(body="{}"), jobs_response])
        http_mocker.post(create_request, HttpResponse(body="{}"))
        http_mocker.post(retired_create_request, HttpResponse(body="{}"))
        http_mocker.get(
            reports_request,
            HttpResponse(body=json.dumps({"error": {"code": 403, "message": "Access denied"}}), status_code=403)
            if report_state == "forbidden"
            else HttpResponse(body=json.dumps({"reports": reports if report_state == "available" else []})),
        )
        http_mocker.get(download_request, HttpResponse(body="date,channel_id,video_id\n20261109,channel-1,video-1\n"))

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.status == (Status.SUCCEEDED if report_state == "available" else Status.FAILED), status.message
        assert "channel_annotations_a1" not in (status.message or "")
        if report_state == "empty":
            assert "channel_basic_a3 - no stream slices were found" in status.message
        elif report_state == "forbidden":
            assert "The YouTube Reporting API denied access: Access denied" in status.message
        http_mocker.assert_number_of_calls(jobs_request, 1 if job_exists else 2)
        http_mocker.assert_number_of_calls(create_request, 0 if job_exists else 1)
        http_mocker.assert_number_of_calls(retired_create_request, 0)
        http_mocker.assert_number_of_calls(reports_request, 1)
        http_mocker.assert_number_of_calls(download_request, 1 if report_state == "available" else 0)
