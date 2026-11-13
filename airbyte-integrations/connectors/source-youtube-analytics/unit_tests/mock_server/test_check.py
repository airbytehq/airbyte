#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging

import freezegun
import requests_mock
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import Status


_API = YoutubeAnalyticsRequestBuilder.BASE_URL
_SUPPORTED_JOB_ID = "job-channel-basic"
_REPORT_ID = "report-channel-basic"
_CHANNEL_BASIC_CSV = (
    "date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,views,comments,likes,dislikes,"
    "videos_added_to_playlists,videos_removed_from_playlists,shares,watch_time_minutes,average_view_duration_seconds,"
    "average_view_duration_percentage,annotation_impressions,annotation_clickable_impressions,annotation_clicks,"
    "annotation_click_through_rate,annotation_closable_impressions,annotation_closes,annotation_close_rate,"
    "card_teaser_impressions,card_teaser_clicks,card_teaser_click_rate,card_impressions,card_clicks,card_click_rate,"
    "subscribers_gained,subscribers_lost,red_views,red_watch_time_minutes,engaged_views\n"
    "20261018,channel-1,video-1,on_demand,subscribed,US" + ",1" * 28 + "\n"
)


@freezegun.freeze_time("2026-10-21T00:00:00Z")
def test_check_succeeds_when_channel_only_lists_supported_report_jobs() -> None:
    """`check` must not depend on a report type YouTube has retired.

    YouTube retired `channel_annotations_a1`: creating a job for it is accepted, but the job
    never shows up in `jobs.list`, so a check on that stream fails with "no stream slices were
    found" and blocks every new source setup. Here the listing only ever contains a job for the
    supported `channel_basic_a3` report, as for a channel after the retirement, and that job has
    one report file.
    """
    config = ConfigBuilder().build()

    with requests_mock.Mocker() as mocker:
        mocker.post(
            YoutubeAnalyticsRequestBuilder.TOKEN_URL,
            json={"access_token": "token", "expires_in": 3600},
        )
        list_jobs = mocker.get(
            f"{_API}/jobs",
            json={"jobs": [{"id": _SUPPORTED_JOB_ID, "reportTypeId": "channel_basic_a3"}]},
        )
        create_job = mocker.post(f"{_API}/jobs", json={"id": "job-retired", "reportTypeId": "channel_annotations_a1"})
        list_reports = mocker.get(
            f"{_API}/jobs/{_SUPPORTED_JOB_ID}/reports",
            json={
                "reports": [
                    {
                        "id": _REPORT_ID,
                        "jobId": _SUPPORTED_JOB_ID,
                        "startTime": "2026-10-18T07:00:00Z",
                        "endTime": "2026-10-19T07:00:00Z",
                        "createTime": "2026-10-20T00:00:00Z",
                        "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(_REPORT_ID),
                    }
                ]
            },
        )
        download = mocker.get(YoutubeAnalyticsRequestBuilder.download_url(_REPORT_ID), text=_CHANNEL_BASIC_CSV)

        status = get_source(config).check(logging.getLogger("test"), config)

    assert status.status == Status.SUCCEEDED, status.message
    # The check uses the existing supported job: it never asks YouTube to create a job for the
    # retired report type, and it reads the supported job's report file.
    assert create_job.call_count == 0
    assert list_jobs.call_count == 1
    assert list_reports.call_count == 1
    assert list_reports.last_request.qs == {"createdafter": ["1990-01-01t00:00:00.000000z"]}
    assert download.call_count == 1
