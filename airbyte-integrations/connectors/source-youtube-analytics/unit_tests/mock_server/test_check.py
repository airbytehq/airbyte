#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging

import freezegun
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


@freezegun.freeze_time("2026-11-10T00:00:00Z")
def test_check_uses_active_basic_report_when_annotations_has_no_reports():
    with HttpMocker() as http_mocker:
        _check_uses_active_basic_report(http_mocker)


def _check_uses_active_basic_report(http_mocker: HttpMocker):
    config = ConfigBuilder().build()
    basic_reports = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint("basic-job")
        .with_created_after("1990-01-01T00:00:00.000000Z")
        .build()
    )
    annotations_reports = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint("annotations-job")
        .with_created_after("1990-01-01T00:00:00.000000Z")
        .build()
    )
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
                        {"id": "annotations-job", "reportTypeId": "channel_annotations_a1"},
                        {"id": "basic-job", "reportTypeId": "channel_basic_a3"},
                    ]
                }
            )
        ),
    )
    http_mocker.get(annotations_reports, HttpResponse(body=json.dumps({"reports": []})))
    http_mocker.get(
        basic_reports,
        HttpResponse(
            body=json.dumps(
                {
                    "reports": [
                        {
                            "id": "basic-report",
                            "jobId": "basic-job",
                            "startTime": "2026-11-07T00:00:00Z",
                            "endTime": "2026-11-08T00:00:00Z",
                            "createTime": "2026-11-09T00:00:00Z",
                            "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("basic-report"),
                        }
                    ]
                }
            )
        ),
    )
    http_mocker.get(
        YoutubeAnalyticsRequestBuilder.download_endpoint("basic-report").build(),
        HttpResponse(body="date,channel_id,views\n20261107,channel-1,1\n"),
    )

    status = get_source(config=config).check(logging.getLogger("airbyte"), config)

    assert status.status == Status.SUCCEEDED, status
    http_mocker.assert_number_of_calls(basic_reports, 1)
    http_mocker.assert_number_of_calls(annotations_reports, 0)
