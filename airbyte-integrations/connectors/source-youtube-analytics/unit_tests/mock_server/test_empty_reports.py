#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import freezegun
import pytest
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_VIDEO_DIMENSIONS = "date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code"
_HEADERS = {
    "channel_annotations_a1": (
        f"{_VIDEO_DIMENSIONS},annotation_type,annotation_id,annotation_impressions,annotation_clickable_impressions,"
        "annotation_closable_impressions,annotation_clicks,annotation_closes,annotation_click_through_rate,annotation_close_rate"
    ),
    "channel_cards_a1": (
        f"{_VIDEO_DIMENSIONS},card_type,card_id,card_impressions,card_teaser_impressions,card_clicks,"
        "card_teaser_clicks,card_click_rate,card_teaser_click_rate"
    ),
    "channel_demographics_a1": f"{_VIDEO_DIMENSIONS},age_group,gender,views_percentage",
    "channel_end_screens_a1": (
        f"{_VIDEO_DIMENSIONS},end_screen_element_type,end_screen_element_id,end_screen_element_impressions,"
        "end_screen_element_clicks,end_screen_element_click_rate"
    ),
    "channel_province_a3": (
        f"{_VIDEO_DIMENSIONS},province_code,engaged_views,views,watch_time_minutes,average_view_duration_seconds,"
        "average_view_duration_percentage,annotation_click_through_rate,annotation_close_rate,annotation_impressions,"
        "annotation_clickable_impressions,annotation_closable_impressions,annotation_clicks,annotation_closes,"
        "card_click_rate,card_teaser_click_rate,card_impressions,card_teaser_impressions,card_clicks,card_teaser_clicks,"
        "red_views,red_watch_time_minutes"
    ),
    "channel_sharing_service_a1": f"{_VIDEO_DIMENSIONS},sharing_service,shares",
    "playlist_province_a2": (
        "date,channel_id,playlist_id,video_id,live_or_on_demand,subscribed_status,country_code,province_code,"
        "engaged_views,views,watch_time_minutes,average_view_duration_seconds,playlist_starts,playlist_saves_added,playlist_saves_removed"
    ),
}
_DIMENSION_VALUES = {
    "date": "20261018",
    "channel_id": "channel-1",
    "video_id": "video-1",
    "playlist_id": "playlist-1",
    "country_code": "US",
    "province_code": "US-CA",
    "age_group": "age25-34",
    "gender": "female",
}


@pytest.mark.parametrize("stream_name", sorted(_HEADERS))
@pytest.mark.parametrize("row_count", [0, 1], ids=["header-only", "one-row"])
@freezegun.freeze_time("2026-10-21T00:00:00Z")
def test_report_csv_completes_with_or_without_data(stream_name: str, row_count: int) -> None:
    header = _HEADERS[stream_name]
    csv = f"{header}\n"
    if row_count:
        csv += ",".join(_DIMENSION_VALUES.get(column, "1") for column in header.split(",")) + "\n"
    config = ConfigBuilder().build()
    state = StateBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    job_id = f"job-{stream_name}"
    report_id = f"report-{stream_name}"

    with HttpMocker() as http_mocker:
        http_mocker.post(
            YoutubeAnalyticsRequestBuilder.token_request(),
            HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
            HttpResponse(body=json.dumps({"jobs": [{"id": job_id, "reportTypeId": stream_name}]})),
        )
        http_mocker.get(
            YoutubeAnalyticsRequestBuilder.reports_endpoint(job_id).with_created_after("1990-01-01T00:00:00.000000Z").build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "reports": [
                            {
                                "id": report_id,
                                "jobId": job_id,
                                "startTime": "2026-10-18T07:00:00Z",
                                "endTime": "2026-10-19T07:00:00Z",
                                "createTime": "2026-10-20T00:00:00Z",
                                "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(report_id),
                            }
                        ]
                    }
                )
            ),
        )
        http_mocker.get(YoutubeAnalyticsRequestBuilder.download_endpoint(report_id).build(), HttpResponse(body=csv))
        output = read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)

    assert output.errors == []
    assert len(output.records) == row_count
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.COMPLETE
    if row_count:
        record = output.records[0].record
        assert record.stream == stream_name
        assert record.data["date"] == 20261018
        assert record.data["video_id"] == "video-1"
        assert set(record.data) == set(header.split(","))
