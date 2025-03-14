#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import json
import unittest
from unittest import TestCase

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)

from .config import BUSINESS_ACCOUNT_ID, ConfigBuilder
from .pagination import NEXT_PAGE_TOKEN, InstagramPaginationStrategy
from .request_builder import RequestBuilder, get_account_request
from .response_builder import get_account_response
from .utils import config, read_output


PARENT_FIELDS = [
    "caption",
    "comments_count",
    "id",
    "ig_id",
    "is_comment_enabled",
    "like_count",
    "media_type",
    "media_product_type",
    "media_url",
    "owner",
    "permalink",
    "shortcode",
    "thumbnail_url",
    "timestamp",
    "username",
    "children",
]
_PARENT_STREAM_NAME = "media"
_STREAM_NAME = "media_insights"


MEDIA_ID_REELS = "84386203808767123"
MEDIA_ID_VIDEO_FEED = "90014330517797123"
MEDIA_ID_VIDEO = "09894619573775123"
MEDIA_ID_CAROUSEL_ALBUM = "66123508374641123"
MEDIA_ID_GENERAL_MEDIA = "35076616084176123"
MEDIA_ID_ERROR_POSTED_BEFORE_BUSINESS = "35076616084176124"
MEDIA_ID_ERROR_WITH_WRONG_PERMISSIONS = "35076616084176125"
MEDIA_ID_ERROR_WITH_WRONG_PERMISSIONS_CODE_10 = "35076616084176126"

REELS = "reels"
VIDEO_FEED = "video_feed"
VIDEO = "video"
CAROUSEL_ALBUM = "carousel_album"
GENERAL_MEDIA = "general_media"
ERROR_POSTED_BEFORE_BUSINESS = "error_posted_before_business"
ERROR_WITH_WRONG_PERMISSIONS = "error_with_wrong_permissions"
ERROR_WITH_WRONG_PERMISSIONS_CODE_10 = "error_with_wrong_permissions_code_10"

_MEDIA_IDS = {
    REELS: MEDIA_ID_REELS,
    VIDEO_FEED: MEDIA_ID_VIDEO_FEED,
    VIDEO: MEDIA_ID_VIDEO,
    CAROUSEL_ALBUM: MEDIA_ID_CAROUSEL_ALBUM,
    GENERAL_MEDIA: MEDIA_ID_GENERAL_MEDIA,
}

METRICS_GENERAL_MEDIA = ["impressions", "reach", "saved", "likes", "comments", "shares", "follows", "profile_visits"]

_METRICS = {
    MEDIA_ID_REELS: [
        "comments",
        "ig_reels_avg_watch_time",
        "ig_reels_video_view_total_time",
        "likes",
        "plays",
        "reach",
        "saved",
        "shares",
        "ig_reels_aggregated_all_plays_count",
        "clips_replays_count",
    ],
    MEDIA_ID_VIDEO_FEED: ["impressions", "reach", "saved"],
    MEDIA_ID_VIDEO: ["impressions", "reach", "saved", "likes", "comments", "shares", "follows", "profile_visits"],
    MEDIA_ID_CAROUSEL_ALBUM: ["impressions", "reach", "saved", "shares", "follows", "profile_visits"],
    MEDIA_ID_GENERAL_MEDIA: METRICS_GENERAL_MEDIA,
    # Reusing general media metrics for error scenarios
    MEDIA_ID_ERROR_POSTED_BEFORE_BUSINESS: METRICS_GENERAL_MEDIA,
    MEDIA_ID_ERROR_WITH_WRONG_PERMISSIONS: METRICS_GENERAL_MEDIA,
    MEDIA_ID_ERROR_WITH_WRONG_PERMISSIONS_CODE_10: METRICS_GENERAL_MEDIA,
}


def _get_parent_request() -> RequestBuilder:
    return RequestBuilder.get_media_endpoint(item_id=BUSINESS_ACCOUNT_ID).with_limit(100).with_fields(PARENT_FIELDS)


def _get_child_request(media_id, metric) -> RequestBuilder:
    return RequestBuilder.get_media_insights_endpoint(item_id=media_id).with_custom_param("metric", metric, with_format=True)


def _get_response(stream_name: str, test: str = None, with_pagination_strategy: bool = True) -> HttpResponseBuilder:
    scenario = ""
    if test:
        scenario = f"_for_{test}"
    kwargs = {
        "response_template": find_template(f"{stream_name}{scenario}", __file__),
        "records_path": FieldPath("data"),
        "pagination_strategy": InstagramPaginationStrategy(request=_get_parent_request().build(), next_page_token=NEXT_PAGE_TOKEN),
    }
    if with_pagination_strategy:
        kwargs["pagination_strategy"] = InstagramPaginationStrategy(request=_get_parent_request().build(), next_page_token=NEXT_PAGE_TOKEN)

    return create_response_builder(**kwargs)


def _record(stream_name: str, test: str = None) -> RecordBuilder:
    scenario = ""
    if test:
        scenario = f"_for_{test}"
    return create_record_builder(
        response_template=find_template(f"{stream_name}{scenario}", __file__),
        records_path=FieldPath("data"),
        record_id_path=FieldPath("id"),
    )


class TestFullRefresh(TestCase):
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_instagram_insights_for_reels(self, http_mocker: HttpMocker) -> None:
        test = REELS
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_parent_request().build(),
            _get_response(stream_name=_PARENT_STREAM_NAME, test=test)
            .with_record(_record(stream_name=_PARENT_STREAM_NAME, test=test))
            .build(),
        )

        http_mocker.get(
            _get_child_request(media_id=MEDIA_ID_REELS, metric=_METRICS[MEDIA_ID_REELS]).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["page_id"]
        assert output.records[0].record.data["business_account_id"]
        assert output.records[0].record.data["id"]
        for metric in _METRICS[MEDIA_ID_REELS]:
            assert metric in output.records[0].record.data

    @HttpMocker()
    def test_instagram_insights_for_video_feed(self, http_mocker: HttpMocker) -> None:
        test = VIDEO_FEED
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_parent_request().build(),
            _get_response(stream_name=_PARENT_STREAM_NAME, test=test)
            .with_record(_record(stream_name=_PARENT_STREAM_NAME, test=test))
            .build(),
        )

        http_mocker.get(
            _get_child_request(media_id=MEDIA_ID_VIDEO_FEED, metric=_METRICS[MEDIA_ID_VIDEO_FEED]).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["page_id"]
        assert output.records[0].record.data["business_account_id"]
        assert output.records[0].record.data["id"]
        for metric in _METRICS[MEDIA_ID_VIDEO_FEED]:
            assert metric in output.records[0].record.data

    @HttpMocker()
    def test_instagram_insights_for_video(self, http_mocker: HttpMocker) -> None:
        test = VIDEO
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_parent_request().build(),
            _get_response(stream_name=_PARENT_STREAM_NAME, test=test)
            .with_record(_record(stream_name=_PARENT_STREAM_NAME, test=test))
            .build(),
        )

        http_mocker.get(
            _get_child_request(media_id=MEDIA_ID_VIDEO, metric=_METRICS[MEDIA_ID_VIDEO]).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["page_id"]
        assert output.records[0].record.data["business_account_id"]
        assert output.records[0].record.data["id"]
        for metric in _METRICS[MEDIA_ID_VIDEO]:
            assert metric in output.records[0].record.data

    @HttpMocker()
    def test_instagram_insights_carousel_album(self, http_mocker: HttpMocker) -> None:
        test = CAROUSEL_ALBUM
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_parent_request().build(),
            _get_response(stream_name=_PARENT_STREAM_NAME, test=test)
            .with_record(_record(stream_name=_PARENT_STREAM_NAME, test=test))
            .build(),
        )

        http_mocker.get(
            _get_child_request(media_id=MEDIA_ID_CAROUSEL_ALBUM, metric=_METRICS[MEDIA_ID_CAROUSEL_ALBUM]).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["page_id"]
        assert output.records[0].record.data["business_account_id"]
        assert output.records[0].record.data["id"]
        for metric in _METRICS[MEDIA_ID_CAROUSEL_ALBUM]:
            assert metric in output.records[0].record.data

    @HttpMocker()
    def test_instagram_insights_general_media(self, http_mocker: HttpMocker) -> None:
        test = GENERAL_MEDIA
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_parent_request().build(),
            _get_response(stream_name=_PARENT_STREAM_NAME, test=test)
            .with_record(_record(stream_name=_PARENT_STREAM_NAME, test=test))
            .build(),
        )

        http_mocker.get(
            _get_child_request(media_id=MEDIA_ID_GENERAL_MEDIA, metric=_METRICS[MEDIA_ID_GENERAL_MEDIA]).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["page_id"]
        assert output.records[0].record.data["business_account_id"]
        assert output.records[0].record.data["id"]
        for metric in _METRICS[MEDIA_ID_GENERAL_MEDIA]:
            assert metric in output.records[0].record.data

    @HttpMocker()
    def test_instagram_insights_error_posted_before_business(self, http_mocker: HttpMocker) -> None:
        test = ERROR_POSTED_BEFORE_BUSINESS
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_parent_request().build(), HttpResponse(json.dumps(find_template(f"{_PARENT_STREAM_NAME}_for_{test}", __file__)), 200)
        )

        http_mocker.get(
            _get_child_request(media_id=MEDIA_ID_GENERAL_MEDIA, metric=_METRICS[MEDIA_ID_GENERAL_MEDIA]).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{GENERAL_MEDIA}", __file__)), 200),
        )

        http_mocker.get(
            _get_child_request(
                media_id=MEDIA_ID_ERROR_POSTED_BEFORE_BUSINESS, metric=_METRICS[MEDIA_ID_ERROR_POSTED_BEFORE_BUSINESS]
            ).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 400),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["page_id"]
        assert output.records[0].record.data["business_account_id"]
        assert output.records[0].record.data["id"]
        for metric in _METRICS[MEDIA_ID_GENERAL_MEDIA]:
            assert metric in output.records[0].record.data

    @HttpMocker()
    def test_instagram_insights_error_with_wrong_permissions(self, http_mocker: HttpMocker) -> None:
        test = ERROR_WITH_WRONG_PERMISSIONS
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_parent_request().build(), HttpResponse(json.dumps(find_template(f"{_PARENT_STREAM_NAME}_for_{test}", __file__)), 200)
        )

        http_mocker.get(
            _get_child_request(media_id=MEDIA_ID_GENERAL_MEDIA, metric=_METRICS[MEDIA_ID_GENERAL_MEDIA]).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{GENERAL_MEDIA}", __file__)), 200),
        )

        http_mocker.get(
            _get_child_request(
                media_id=MEDIA_ID_ERROR_WITH_WRONG_PERMISSIONS, metric=_METRICS[MEDIA_ID_ERROR_WITH_WRONG_PERMISSIONS]
            ).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 400),
        )

        output = self._read(config_=config())
        # error was ignored and correct record was processed
        assert len(output.records) == 1
        assert output.records[0].record.data["page_id"]
        assert output.records[0].record.data["business_account_id"]
        assert output.records[0].record.data["id"]
        for metric in _METRICS[MEDIA_ID_GENERAL_MEDIA]:
            assert metric in output.records[0].record.data

    @HttpMocker()
    def test_instagram_insights_error_with_wrong_permissions_code_10(self, http_mocker: HttpMocker) -> None:
        test = ERROR_WITH_WRONG_PERMISSIONS_CODE_10
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_parent_request().build(), HttpResponse(json.dumps(find_template(f"{_PARENT_STREAM_NAME}_for_{test}", __file__)), 200)
        )

        http_mocker.get(
            _get_child_request(media_id=MEDIA_ID_GENERAL_MEDIA, metric=_METRICS[MEDIA_ID_GENERAL_MEDIA]).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{GENERAL_MEDIA}", __file__)), 200),
        )

        http_mocker.get(
            _get_child_request(
                media_id=MEDIA_ID_ERROR_WITH_WRONG_PERMISSIONS_CODE_10, metric=_METRICS[MEDIA_ID_ERROR_WITH_WRONG_PERMISSIONS_CODE_10]
            ).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 400),
        )

        output = self._read(config_=config())
        # error was ignored and correct record was processed
        assert len(output.records) == 1
        assert output.records[0].record.data["page_id"]
        assert output.records[0].record.data["business_account_id"]
        assert output.records[0].record.data["id"]
        for metric in _METRICS[MEDIA_ID_GENERAL_MEDIA]:
            assert metric in output.records[0].record.data
