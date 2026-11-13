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


_CREATED_AFTER = "1990-01-01T00:00:00.000000Z"


@freezegun.freeze_time("2026-10-21T00:00:00Z")
def test_check_succeeds_when_the_retired_annotations_report_has_no_files() -> None:
    """YouTube no longer lists `channel_annotations_a1` among its channel reports, so its job has
    no report files to list. The connection check must not depend on that report: an account
    whose `channel_basic_a3` job has a report file passes the check.
    """
    config = ConfigBuilder().build()
    annotations_reports = YoutubeAnalyticsRequestBuilder.reports_endpoint("job-annotations").with_created_after(_CREATED_AFTER).build()
    basic_reports = YoutubeAnalyticsRequestBuilder.reports_endpoint("job-basic").with_created_after(_CREATED_AFTER).build()
    basic_download = YoutubeAnalyticsRequestBuilder.download_endpoint("report-basic").build()

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
        # The API returns {} rather than {"reports": []} when a job has no report files.
        http_mocker.get(annotations_reports, HttpResponse(body=json.dumps({})))
        http_mocker.get(
            basic_reports,
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
        http_mocker.get(basic_download, HttpResponse(body="date,channel_id,video_id,views\n20261018,channel-1,video-1,7\n"))

        status = get_source(config).check(logging.getLogger("airbyte"), config)

        assert status.status == Status.SUCCEEDED, status.message
        http_mocker.assert_number_of_calls(annotations_reports, 0)
        http_mocker.assert_number_of_calls(basic_reports, 1)
        http_mocker.assert_number_of_calls(basic_download, 1)
