#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import freezegun
import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.entrypoint_wrapper import _run_command, make_file
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@freezegun.freeze_time("2026-11-05T00:00:00Z")
@pytest.mark.parametrize("creation_status", [400, 200], ids=["unsupported-report-type", "job-not-materialized"])
def test_check_succeeds_without_a_retired_annotations_job(tmp_path, creation_status):
    """400 models an unsupported type; 200 with no listed job isolates the no-slices failure.

    The empty creation response is a fault-injection scenario, not a captured YouTube response.
    """
    config = ConfigBuilder().build()
    token_request = YoutubeAnalyticsRequestBuilder.token_request()
    jobs_request = YoutubeAnalyticsRequestBuilder.jobs_endpoint().build()
    create_annotations_request = HttpRequest(
        url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
        query_params={},
        body={"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"},
    )
    reports_request = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint("basic-job")
        .with_created_after("1990-01-01T00:00:00.000000Z")
        .build()
    )
    download_request = YoutubeAnalyticsRequestBuilder.download_endpoint("basic-report").build()

    with HttpMocker() as http_mocker:
        http_mocker.get(
            jobs_request,
            HttpResponse(body=json.dumps({"jobs": [{"id": "basic-job", "reportTypeId": "channel_basic_a3"}]})),
        )
        http_mocker.post(
            create_annotations_request,
            HttpResponse(
                status_code=creation_status,
                body=json.dumps(
                    {"error": {"code": 400, "status": "INVALID_ARGUMENT", "message": "Unsupported reportTypeId: channel_annotations_a1"}}
                    if creation_status == 400
                    else {}
                ),
            ),
        )
        http_mocker.post(token_request, HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})))
        http_mocker.get(
            reports_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": "basic-report",
                                "jobId": "basic-job",
                                "startTime": "2026-11-03T00:00:00Z",
                                "endTime": "2026-11-04T00:00:00Z",
                                "createTime": "2026-11-04T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("basic-report"),
                            }
                        ]
                    }
                )
            ),
        )
        http_mocker.get(download_request, HttpResponse(body="date,channel_id,views\n20261103,channel-1,3\n"))

        output = _run_command(get_source(config), ["check", "--config", make_file(tmp_path / "config.json", config)])

        assert len(output.connection_status_messages) == 1
        connection_status = output.connection_status_messages[0].connectionStatus
        assert connection_status.status == Status.SUCCEEDED, connection_status.message
        assert output.errors == []
        http_mocker.assert_number_of_calls(token_request, 3)
        http_mocker.assert_number_of_calls(jobs_request, 1)
        http_mocker.assert_number_of_calls(reports_request, 1)
        http_mocker.assert_number_of_calls(download_request, 1)
        http_mocker.assert_number_of_calls(create_annotations_request, 0)
