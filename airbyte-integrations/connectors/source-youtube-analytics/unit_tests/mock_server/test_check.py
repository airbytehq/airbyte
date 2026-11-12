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


_BASIC_HEADER = (
    "date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,engaged_views,views,comments,likes,"
    "dislikes,videos_added_to_playlists,videos_removed_from_playlists,shares,watch_time_minutes,"
    "average_view_duration_seconds,average_view_duration_percentage,annotation_click_through_rate,annotation_close_rate,"
    "annotation_impressions,annotation_clickable_impressions,annotation_closable_impressions,annotation_clicks,"
    "annotation_closes,card_click_rate,card_teaser_click_rate,card_impressions,card_teaser_impressions,card_clicks,"
    "card_teaser_clicks,subscribers_gained,subscribers_lost,red_views,red_watch_time_minutes"
)


def test_check_succeeds_without_touching_the_retired_annotations_report() -> None:
    """`check` reads `channel_basic_a3`, so a retired report type with no files cannot block setup.

    The account has a job for `channel_annotations_a1`, but nothing is mocked under it: `HttpMocker`
    rejects any request to that job, and requires every request mocked below to be made.
    """
    config = ConfigBuilder().build()
    basic_row = ",".join("20261018" if column == "date" else "1" for column in _BASIC_HEADER.split(","))

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
            YoutubeAnalyticsRequestBuilder.reports_endpoint("job-basic").with_created_after("1990-01-01T00:00:00.000000Z").build(),
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
            YoutubeAnalyticsRequestBuilder.download_endpoint("report-basic").build(),
            HttpResponse(body=f"{_BASIC_HEADER}\n{basic_row}\n"),
        )

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED
    assert status.message is None
