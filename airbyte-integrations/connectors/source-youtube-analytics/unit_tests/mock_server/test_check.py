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


_BASIC_HEADER = (
    "date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,engaged_views,views,comments,likes,"
    "dislikes,shares,watch_time_minutes,average_view_duration_seconds,average_view_duration_percentage"
)


@freezegun.freeze_time("2026-10-21T00:00:00Z")
def test_check_succeeds_when_only_the_basic_report_job_has_report_files() -> None:
    """YouTube has not generated any `channel_annotations_a1` report file for this channel, but
    `channel_basic_a3` files exist. The connection check has to pass by reading `channel_basic_a3`
    and must not depend on the annotations job."""
    config = ConfigBuilder().build()
    basic_reports_request = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint("job-basic").with_created_after("1990-01-01T00:00:00.000000Z").build()
    )
    annotations_reports_request = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint("job-annotations").with_created_after("1990-01-01T00:00:00.000000Z").build()
    )
    download_request = YoutubeAnalyticsRequestBuilder.download_endpoint("report-basic").build()

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
        # The API returns {} instead of {"reports": []} when a job has no report files.
        http_mocker.get(annotations_reports_request, HttpResponse(body=json.dumps({})))
        http_mocker.get(
            basic_reports_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": "report-basic",
                                "jobId": "job-basic",
                                "startTime": "2026-10-18T07:00:00Z",
                                "endTime": "2026-10-19T07:00:00Z",
                                "createTime": "2026-10-20T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url("report-basic"),
                            }
                        ]
                    }
                )
            ),
        )
        http_mocker.get(
            download_request,
            HttpResponse(body=f"{_BASIC_HEADER}\n20261018,channel-1,video-1,on_demand,subscribed,US,1,1,0,0,0,0,1.0,60.0,50.0\n"),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.status == Status.SUCCEEDED, status.message
        http_mocker.assert_number_of_calls(basic_reports_request, 1)
        http_mocker.assert_number_of_calls(download_request, 1)
        http_mocker.assert_number_of_calls(annotations_reports_request, 0)
