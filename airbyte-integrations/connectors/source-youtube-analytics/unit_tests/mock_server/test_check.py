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


_CHECK_REPORT_TYPE = "channel_basic_a3"
_JOB_ID = "job-channel-basic"
_REPORT_ID = "report-channel-basic"


@freezegun.freeze_time("2026-10-21T00:00:00Z")
def test_check_succeeds_using_a_supported_report_type() -> None:
    """`check` must probe a report type YouTube still supports.

    YouTube retired `channel_annotations_a1` (October 2025): no reporting job exists or can be
    created for it, so a check against that report type finds no stream slices and every new
    source setup fails. The account here only has a job for `channel_basic_a3`; `check` must
    succeed against it without trying to create a job for any other report type.
    """
    config = ConfigBuilder().build()
    source = get_source(config)

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(body=json.dumps({"jobs": [{"id": _JOB_ID, "reportTypeId": _CHECK_REPORT_TYPE}]})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint(_JOB_ID).with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": _REPORT_ID,
                                "jobId": _JOB_ID,
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
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.download_endpoint(_REPORT_ID).build(),
            HttpResponse(
                body=(
                    "date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,views\n"
                    "20261018,channel-1,video-1,on_demand,subscribed,US,5\n"
                )
            ),
        )

        connection_status = source.check(logging.getLogger("test"), config)

    assert connection_status.status == Status.SUCCEEDED, connection_status.message
