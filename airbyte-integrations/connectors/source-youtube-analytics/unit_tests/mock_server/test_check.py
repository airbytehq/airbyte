#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def test_check_succeeds_with_only_supported_reporting_jobs(tmp_path):
    config = ConfigBuilder().build()
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))

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
            HttpRequest(
                url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
                body=json.dumps({"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"}),
            ),
            HttpResponse(body="{}"),
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
                                "startTime": "2026-11-10T00:00:00Z",
                                "endTime": "2026-11-11T00:00:00Z",
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
            HttpResponse(body="date,channel_id,views\n20261110,channel-1,1\n"),
        )

        entrypoint = AirbyteEntrypoint(get_source(config))
        messages = [json.loads(message) for message in entrypoint.run(entrypoint.parse_args(["check", "--config", str(config_path)]))]

    statuses = [message["connectionStatus"] for message in messages if message["type"] == "CONNECTION_STATUS"]
    assert len(statuses) == 1
    assert statuses[0]["status"] == Status.SUCCEEDED.value, statuses[0]
