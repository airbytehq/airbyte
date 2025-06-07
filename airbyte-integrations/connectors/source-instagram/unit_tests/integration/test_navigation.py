#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import json
import unittest
from unittest import TestCase

import pytest

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
from airbyte_protocol.models import SyncMode

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
_STREAM_NAME = "navigation"


MEDIA_ID_STORY = "18026588782970000"
STORY = "story"


_METRICS = {
    MEDIA_ID_STORY: ["navigation"],
}


def _get_parent_request() -> RequestBuilder:
    return RequestBuilder.get_media_endpoint(item_id=BUSINESS_ACCOUNT_ID).with_limit(100).with_fields(PARENT_FIELDS)


def _get_child_request(media_id, metric) -> RequestBuilder:
    return (
        RequestBuilder.get_navigation_endpoint(item_id=media_id)
        .with_custom_param("metric", metric, with_format=True)
        .with_custom_param("breakdown", "story_navigation_action_type")
    )


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
    def test_instagram_insights_for_navigation(self, http_mocker: HttpMocker) -> None:
        test = STORY
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
            _get_child_request(media_id=MEDIA_ID_STORY, metric=_METRICS[MEDIA_ID_STORY]).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["page_id"]
        assert output.records[0].record.data["business_account_id"]
        assert output.records[0].record.data["id"]
        for breakdown in ["action_type"]:
            assert breakdown in output.records[0].record.data["breakdown"]
        assert output.records[0].record.data["value"].get("tap_forward") == 2
