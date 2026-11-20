#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import freezegun
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


@freezegun.freeze_time("2026-10-21T00:00:00Z")
def test_report_download_permission_denied_is_config_error() -> None:
    stream_name = "channel_basic_a3"
    config = ConfigBuilder().build()
    state = StateBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    job_id = f"job-{stream_name}"
    report_id = f"report-{stream_name}"

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(body=json.dumps({"jobs": [{"id": job_id, "reportTypeId": stream_name}]})),
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
            HttpResponse(
                status_code=403,
                body=json.dumps({"error": {"code": 403, "message": "The caller does not have permission", "status": "PERMISSION_DENIED"}}),
            ),
        )
        output = read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)

    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.INCOMPLETE
    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert "The YouTube Reporting API denied access" in error.message
