#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging

from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


_START = "1990-01-01T00:00:00.000000Z"


def _report(report_id: str, job_id: str) -> dict:
    return {
        "id": report_id,
        "jobId": job_id,
        "startTime": "2026-10-18T07:00:00Z",
        "endTime": "2026-10-19T07:00:00Z",
        "createTime": "2026-10-20T00:00:00Z",
        "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(report_id),
    }


def test_check_succeeds_when_the_retired_annotations_report_has_no_files() -> None:
    """YouTube retired `channel_annotations_a1` on 2025-10-31 and no longer issues report files for it.

    A channel that has a supported `channel_basic_a3` report but no annotations report files
    must still pass `check`, so the check must not depend on the retired report type.
    """
    config = ConfigBuilder().build()

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
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint("job-annotations").with_created_after(_START).build(),
            HttpResponse(body=json.dumps({})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint("job-basic").with_created_after(_START).build(),
            HttpResponse(body=json.dumps({"reports": [_report("report-basic", "job-basic")]})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint("report-basic").build(),
            HttpResponse(body="date,channel_id,video_id,views\n20261018,channel-1,video-1,7\n"),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED, status.message
