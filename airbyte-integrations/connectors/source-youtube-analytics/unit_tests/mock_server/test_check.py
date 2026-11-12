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


_BASIC_JOB_ID = "job-channel-basic"
_ANNOTATIONS_JOB_ID = "job-channel-annotations"
_BASIC_REPORT_ID = "report-channel-basic"
_BASIC_CSV = (
    "date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,views\n"
    "20261018,channel-1,video-1,on_demand,subscribed,US,5\n"
)


@freezegun.freeze_time("2026-11-12T00:00:00Z")
def test_check_succeeds_when_the_retired_annotations_report_has_no_files() -> None:
    """YouTube retired `channel_annotations_a1` on 2025-10-31 and no longer generates its files.

    An account that still has the old annotations job gets an empty report list for it, so a
    check that reads that stream finds no partitions and fails setup. Check must read a report
    type YouTube still generates, and must not touch the retired one at all.
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
        # No mock for the annotations job's report listing: HttpMocker fails any unmatched request,
        # so check must never ask for the retired report type's files.
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
        http_mocker.get(YoutubeAnalyticsRequestBuilder.download_endpoint(_BASIC_REPORT_ID).build(), HttpResponse(body=_BASIC_CSV))

        status = get_source(config).check(logging.getLogger("test"), config)

        assert status.status == Status.SUCCEEDED, status.message
