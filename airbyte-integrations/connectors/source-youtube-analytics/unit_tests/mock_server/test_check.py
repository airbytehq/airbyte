#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

import freezegun
import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.entrypoint_wrapper import _run_command, make_file
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("csv", ["date,channel_id,views\n", "date,channel_id,views\n20261109,channel-1,3\n"], ids=["header-only", "one-row"])
@freezegun.freeze_time("2026-11-12T00:00:00Z")
def test_check_succeeds_when_annotations_report_type_is_retired(tmp_path: Path, csv: str) -> None:
    config = ConfigBuilder().build()
    config_path = make_file(tmp_path / "config.json", config)
    job_id = "job-basic"
    report_id = "report-basic"

    with HttpMocker() as http_mocker:
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(
                body=json.dumps(
                    {"jobs": [{"id": job_id, "reportTypeId": "channel_basic_a3"}, {"id": "job-combined", "reportTypeId": "channel_combined_a3"}]}
                )
            ),
        )
        http_mocker.post(
            HttpRequest(
                url=f"{YoutubeAnalyticsRequestBuilder.BASE_URL}/jobs",
                body={"name": "Airbyte reporting job", "reportTypeId": "channel_annotations_a1"},
            ),
            HttpResponse(
                status_code=400,
                body=json.dumps({"error": {"code": 400, "message": "Report type is not supported.", "status": "INVALID_ARGUMENT"}}),
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint(job_id).with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": report_id,
                                "jobId": job_id,
                                "startTime": "2026-11-09T00:00:00Z",
                                "endTime": "2026-11-10T00:00:00Z",
                                "createTime": "2026-11-11T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(report_id),
                            }
                        ]
                    }
                )
            ),
        )
        http_mocker.get(YoutubeAnalyticsRequestBuilder.download_endpoint(report_id).build(), HttpResponse(body=csv))
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )

        output = _run_command(get_source(config=config), ["check", "--config", config_path])

    assert len(output.connection_status_messages) == 1
    assert output.connection_status_messages[0].connectionStatus.status == Status.SUCCEEDED
