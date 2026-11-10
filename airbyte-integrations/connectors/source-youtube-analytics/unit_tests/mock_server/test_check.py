#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import freezegun
import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import Status, Type
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize(
    "reports_status,has_report", [(200, True), (200, False), (403, False)], ids=["report-data", "empty-reports", "reports-denied"]
)
@freezegun.freeze_time("2026-10-21T00:00:00Z")
def test_check_uses_supported_report_when_annotations_are_retired(reports_status: int, has_report: bool) -> None:
    config = ConfigBuilder().build()
    source = get_source(config=config)
    entrypoint = AirbyteEntrypoint(source)
    reports_request = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint("job-channel-basic")
        .with_created_after("1990-01-01T00:00:00.000000Z")
        .build()
    )
    retired_job_request = HttpRequest(
        url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
        body=json.dumps({"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"}),
    )
    reports_body = {}
    if has_report:
        reports_body = {
            "reports": [
                {
                    "id": "report-basic",
                    "jobId": "job-channel-basic",
                    "startTime": "2026-10-18T07:00:00Z",
                    "endTime": "2026-10-19T07:00:00Z",
                    "createTime": "2026-10-20T00:00:00Z",
                    "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("report-basic"),
                }
            ]
        }

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(body=json.dumps({"jobs": [{"id": "job-channel-basic", "reportTypeId": "channel_basic_a3"}]})),
        )
        http_mocker.post(
            retired_job_request,
            HttpResponse(
                status_code=400,
                body=json.dumps({"error": {"code": 400, "status": "INVALID_ARGUMENT", "message": "Unknown reportTypeId"}}),
            ),
        )
        http_mocker.get(
            reports_request,
            HttpResponse(
                status_code=reports_status,
                body=json.dumps(reports_body if reports_status == 200 else {"error": {"code": 403, "message": "Access denied"}}),
            ),
        )
        if has_report:
            http_mocker.get(
                YoutubeAnalyticsRequestBuilder.download_endpoint("report-basic").build(),
                HttpResponse(body="date,channel_id,video_id,views\n20261018,channel-1,video-1,1\n"),
            )
        messages = list(entrypoint.check(source.spec(entrypoint.logger), config))
        connection_status = next(message.connectionStatus for message in messages if message.type == Type.CONNECTION_STATUS)

        expected_status = Status.SUCCEEDED if has_report else Status.FAILED
        assert connection_status.status == expected_status, connection_status.message
        http_mocker.assert_number_of_calls(reports_request, 1)
        http_mocker.assert_number_of_calls(retired_job_request, 0)
        if reports_status == 403:
            assert "The YouTube Reporting API denied access: Access denied" in connection_status.message
        elif not has_report:
            assert "Cannot attempt to connect to stream channel_basic_a3 - no stream slices were found" in connection_status.message
