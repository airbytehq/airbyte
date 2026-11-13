#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import Status
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("has_rows", [True, False], ids=["populated-report", "header-only-report"])
def test_check_succeeds_without_retired_annotation_jobs(tmp_path, has_rows: bool) -> None:
    config = ConfigBuilder().build()
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    job_id = "job-channel-basic-a3"
    report_id = "basic-report"
    reports_request = YoutubeAnalyticsRequestBuilder.reports_endpoint(job_id).with_created_after("1990-01-01T00:00:00.000000Z").build()
    retired_job_request = HttpRequest(
        url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
        body={"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"},
    )
    reports = [
        {
            "id": report_id,
            "jobId": job_id,
            "startTime": "2026-11-09T00:00:00Z",
            "endTime": "2026-11-10T00:00:00Z",
            "createTime": "2026-11-11T00:00:00Z",
            "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(report_id),
        }
    ]

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
                    {"error": {"code": 400, "status": "INVALID_ARGUMENT", "message": "Report type channel_annotations_a1 is deprecated."}}
                ),
            ),
        )
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(reports_request, HttpResponse(body=json.dumps({"reports": reports})))
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint(report_id).build(),
            HttpResponse(body="date,channel_id,views\n" + ("20261109,channel-1,1\n" if has_rows else "")),
        )

        entrypoint = AirbyteEntrypoint(get_source(config=config))
        output = EntrypointOutput(messages=list(entrypoint.run(AirbyteEntrypoint.parse_args(["check", "--config", str(config_path)]))))

        assert output.connection_status_messages[0].connectionStatus.status == Status.SUCCEEDED
        http_mocker.assert_number_of_calls(reports_request, 1)
        http_mocker.assert_number_of_calls(retired_job_request, 0)
