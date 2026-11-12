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


_RETIRED_JOB_ID = "job-channel_annotations_a1"
_BASIC_JOB_ID = "job-channel_basic_a3"
_BASIC_REPORT_ID = "report-channel_basic_a3"
_FIRST_CREATE_TIME = "1990-01-01T00:00:00.000000Z"


def test_check_succeeds_when_the_retired_annotations_report_has_no_files() -> None:
    """YouTube no longer generates files for `channel_annotations_a1`, so its job lists no reports.

    Source setup must not depend on that report: the check passes on `channel_basic_a3`, whose
    job has a report file, and never asks for the annotations job's reports.
    """
    config = ConfigBuilder().build()
    retired_reports_request = (
        YoutubeAnalyticsRequestBuilder.reports_endpoint(_RETIRED_JOB_ID).with_created_after(_FIRST_CREATE_TIME).build()
    )

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
                            {"id": _RETIRED_JOB_ID, "reportTypeId": "channel_annotations_a1"},
                            {"id": _BASIC_JOB_ID, "reportTypeId": "channel_basic_a3"},
                        ]
                    }
                )
            ),
        )
        # The API returns {} instead of {"reports": []} when a job has no report files.
        http_mocker.get(retired_reports_request, HttpResponse(body=json.dumps({})))
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint(_BASIC_JOB_ID).with_created_after(_FIRST_CREATE_TIME).build(),
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
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint(_BASIC_REPORT_ID).build(),
            HttpResponse(
                body="date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,views\n"
                "20261018,channel-1,video-1,on_demand,subscribed,US,1\n"
            ),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.message is None
        assert status.status == Status.SUCCEEDED
        http_mocker.assert_number_of_calls(retired_reports_request, 0)
