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
_BASIC_REPORT_ID = "report-channel_basic_a3"


def test_check_succeeds_when_only_a_retired_report_type_has_no_report_files() -> None:
    """Connection check must not depend on a report type YouTube has retired.

    The account has a healthy `channel_basic_a3` job with a report file, and a leftover
    `channel_annotations_a1` job. YouTube no longer generates files for the latter, so its
    report listing is not mocked: any request for it is unmatched and fails the check, as does
    any attempt to create a job. The matchers registered below are therefore the exact set of
    requests the check may send.
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
                            {"id": "job-channel_annotations_a1", "reportTypeId": "channel_annotations_a1"},
                            {"id": _BASIC_JOB_ID, "reportTypeId": "channel_basic_a3"},
                        ]
                    }
                )
            ),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint(_BASIC_JOB_ID).with_created_after("1990-01-01T00:00:00.000000Z").build(),
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
            HttpResponse(body="date,channel_id,video_id,views\n20261018,channel-1,video-1,1\n"),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.status == Status.SUCCEEDED, status.message
