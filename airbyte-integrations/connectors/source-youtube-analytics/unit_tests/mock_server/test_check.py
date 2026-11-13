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


_BASIC_JOB_ID = "job-channel_basic_a3"
_ANNOTATIONS_JOB_ID = "job-channel_annotations_a1"
_REPORT_ID = "report-channel_basic_a3"
_BASIC_CSV = (
    "date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,views\n"
    "20261018,channel-1,video-1,on_demand,subscribed,US,10\n"
)


def test_check_succeeds_when_deprecated_annotations_report_has_no_reports() -> None:
    """YouTube retired `channel_annotations_a1` on 2025-10-31 and no longer generates its reports.

    `check` must probe a report type that YouTube still generates (`channel_basic_a3`) instead
    of failing with "no stream slices were found" on the retired annotations report.
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
                            {"id": _ANNOTATIONS_JOB_ID, "reportTypeId": "channel_annotations_a1"},
                            {"id": _BASIC_JOB_ID, "reportTypeId": "channel_basic_a3"},
                        ]
                    }
                )
            ),
        )
        # The retired report type's job never gets new report files.
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint(_ANNOTATIONS_JOB_ID).with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(body=json.dumps({})),
        )
        basic_reports_request = (
            YoutubeAnalyticsRequestBuilder.reports_endpoint(_BASIC_JOB_ID).with_created_after("1990-01-01T00:00:00.000000Z").build()
        )
        http_mocker.get(
            basic_reports_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": _REPORT_ID,
                                "jobId": _BASIC_JOB_ID,
                                "startTime": "2026-10-18T07:00:00Z",
                                "endTime": "2026-10-19T07:00:00Z",
                                "createTime": "2026-10-20T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(_REPORT_ID),
                            }
                        ]
                    }
                )
            ),
        )
        download_request = YoutubeAnalyticsRequestBuilder.download_endpoint(_REPORT_ID).build()
        http_mocker.get(download_request, HttpResponse(body=_BASIC_CSV))

        connection_status = get_source(config=config).check(logging.getLogger("test"), config)

        assert connection_status.status == Status.SUCCEEDED, connection_status.message
        http_mocker.assert_number_of_calls(basic_reports_request, 1)
        http_mocker.assert_number_of_calls(download_request, 1)
