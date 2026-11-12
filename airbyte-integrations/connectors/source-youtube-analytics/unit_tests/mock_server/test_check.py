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
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@freezegun.freeze_time("2026-11-11T00:00:00Z")
def test_check_succeeds_without_a_retired_annotations_job(tmp_path) -> None:
    config = ConfigBuilder().build()
    config_path = make_file(tmp_path / "config.json", config)

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(body=json.dumps({"jobs": [{"id": "basic-job", "reportTypeId": "channel_basic_a3"}]})),
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
            YoutubeAnalyticsRequestBuilder.reports_endpoint("basic-job").with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": "basic-report",
                                "jobId": "basic-job",
                                "startTime": "2026-11-08T00:00:00Z",
                                "endTime": "2026-11-09T00:00:00Z",
                                "createTime": "2026-11-10T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("basic-report"),
                            }
                        ]
                    }
                )
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint("basic-report").build(),
            HttpResponse(body="date,channel_id,views\n20261108,channel-1,3\n"),
        )
        output = _run_command(get_source(config), ["check", "--config", config_path])

    assert len(output.connection_status_messages) == 1
    assert output.connection_status_messages[0].connectionStatus.status == Status.SUCCEEDED
