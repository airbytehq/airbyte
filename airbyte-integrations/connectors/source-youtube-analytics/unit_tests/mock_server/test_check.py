#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import freezegun
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.entrypoint_wrapper import _run_command, make_file
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


@freezegun.freeze_time("2026-10-21T00:00:00Z")
def test_check_succeeds_when_annotations_reports_are_empty(tmp_path) -> None:
    config = ConfigBuilder().build()
    annotations_request = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint("job-annotations")
        .with_created_after("1990-01-01T00:00:00.000000Z")
        .build()
    )
    report_id = "report-basic"

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "jobs": [
                            {"id": "job-annotations", "reportTypeId": "channel_annotations_a1"},
                            {"id": "job-basic", "reportTypeId": "channel_basic_a3"},
                        ]
                    }
                )
            ),
        )
        http_mocker.get(annotations_request, HttpResponse(body="{}"))
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint("job-basic")
            .with_created_after("1990-01-01T00:00:00.000000Z")
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": report_id,
                                "jobId": "job-basic",
                                "startTime": "2026-10-18T07:00:00Z",
                                "endTime": "2026-10-19T07:00:00Z",
                                "createTime": "2026-10-20T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(report_id),
                            }
                        ]
                    }
                )
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint(report_id).build(),
            HttpResponse(body="date,channel_id,video_id\n"),
        )
        config_file = make_file(tmp_path / "config.json", config)
        output = _run_command(get_source(config=config), ["check", "--config", config_file])

        status = output.connection_status_messages[0].connectionStatus
        assert status.status == Status.SUCCEEDED, status.message
        http_mocker.assert_number_of_calls(annotations_request, 0)
