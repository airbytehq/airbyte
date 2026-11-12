#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Mock server tests for the connection check.

YouTube retired the `channel_annotations_a1` report type: it is no longer listed among the
channel reports, and an existing job for it gets no new report files, so a check against it
finds no report to read. The check has to use a report type YouTube still generates daily.
https://developers.google.com/youtube/reporting/v1/reports/channel_reports
"""

import json
import logging

import freezegun
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


_DEFAULT_START_TIME = "1990-01-01T00:00:00.000000Z"
_BASIC_JOB_ID = "job-channel_basic_a3"
_BASIC_REPORT_ID = "report-channel_basic_a3"


@freezegun.freeze_time("2026-10-21T00:00:00Z")
def test_check_succeeds_when_the_retired_annotations_report_has_no_files() -> None:
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
                            {"id": "job-channel_annotations_a1", "reportTypeId": "channel_annotations_a1"},
                            {"id": _BASIC_JOB_ID, "reportTypeId": "channel_basic_a3"},
                        ]
                    }
                )
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint("job-channel_annotations_a1").with_created_after(_DEFAULT_START_TIME).build(),
            HttpResponse(body=json.dumps({})),
        )
        basic_reports = YoutubeAnalyticsRequestBuilder.reports_endpoint(_BASIC_JOB_ID).with_created_after(_DEFAULT_START_TIME).build()
        http_mocker.get(
            basic_reports,
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": _BASIC_REPORT_ID,
                                "jobId": _BASIC_JOB_ID,
                                "startTime": "2026-10-18T07:00:00Z",
                                "endTime": "2026-10-19T07:00:00Z",
                                "createTime": "2026-10-20T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(_BASIC_REPORT_ID),
                            }
                        ]
                    }
                )
            ),
        )
        download = YoutubeAnalyticsRequestBuilder.download_endpoint(_BASIC_REPORT_ID).build()
        http_mocker.get(download, HttpResponse(body="date,channel_id,video_id,views\n20261018,channel-1,video-1,3\n"))

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.message is None
        assert status.status == Status.SUCCEEDED
        http_mocker.assert_number_of_calls(basic_reports, 1)
        http_mocker.assert_number_of_calls(download, 1)
