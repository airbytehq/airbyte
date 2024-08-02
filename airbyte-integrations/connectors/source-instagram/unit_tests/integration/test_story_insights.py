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
    "id",
    "ig_id",
    "like_count",
    "media_type",
    "media_product_type",
    "media_url",
    "owner",
    "permalink",
    "shortcode",
    "thumbnail_url",
    "timestamp",
    "username"
]
_PARENT_STREAM_NAME = 'stories'
_STREAM_NAME = "story_insights"

STORIES_ID = "3874523487643"
STORIES_ID_ERROR_CODE_10 = "3874523487644"

HAPPY_PATH = 'story_insights_happy_path'
ERROR_10 = 'story_insights_error_code_10'

_METRICS = ["impressions", "reach", "replies", "follows", "profile_visits", "shares", "total_interactions"]



def _get_parent_request() -> RequestBuilder:
    return (
        RequestBuilder.get_stories_endpoint(item_id=BUSINESS_ACCOUNT_ID)
        .with_limit(100)
        .with_fields(PARENT_FIELDS)
    )


def _get_child_request(media_id, metric) -> RequestBuilder:
    return (
        RequestBuilder.get_media_insights_endpoint(item_id=media_id)
        .with_custom_param("metric", metric, with_format=True)
    )


def _get_response(stream_name: str, test: str = None, with_pagination_strategy: bool = True) -> HttpResponseBuilder:
    scenario = ''
    if test:
        scenario = f'_for_{test}'
    kwargs = {
        "response_template": find_template(f"{stream_name}{scenario}", __file__),
        "records_path": FieldPath("data"),
        "pagination_strategy": InstagramPaginationStrategy(request=_get_parent_request().build(), next_page_token=NEXT_PAGE_TOKEN),
    }
    if with_pagination_strategy:
        kwargs["pagination_strategy"] = InstagramPaginationStrategy(request=_get_parent_request().build(), next_page_token=NEXT_PAGE_TOKEN)

    return create_response_builder(
        **kwargs
    )


def _record(stream_name: str, test: str = None) -> RecordBuilder:
    scenario = ''
    if test:
        scenario = f'_for_{test}'
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
    def test_instagram_story_insights(self, http_mocker: HttpMocker) -> None:
        test = HAPPY_PATH
        # Mocking API stream
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        # Mocking parent stream
        http_mocker.get(
            _get_parent_request().build(),
            _get_response(stream_name=_PARENT_STREAM_NAME, test=test).with_record(_record(stream_name=_PARENT_STREAM_NAME, test=test)).build(),
        )

        http_mocker.get(
            _get_child_request(media_id=STORIES_ID, metric=_METRICS).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 200)
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["page_id"]
        assert output.records[0].record.data["business_account_id"]
        assert output.records[0].record.data["id"]
        for metric in _METRICS:
            assert metric in output.records[0].record.data


    @HttpMocker()
    def test_instagram_story_insights_for_error_code_30(self, http_mocker: HttpMocker) -> None:
        test = ERROR_10
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        # Mocking parent stream
        http_mocker.get(
            _get_parent_request().build(),
            HttpResponse(json.dumps(find_template(f"{_PARENT_STREAM_NAME}_for_{test}", __file__)), 200)
        )
        # Good response
        http_mocker.get(
            _get_child_request(media_id=STORIES_ID, metric=_METRICS).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{HAPPY_PATH}", __file__)), 200)
        )
        # error 10
        http_mocker.get(
            _get_child_request(media_id=STORIES_ID_ERROR_CODE_10, metric=_METRICS).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 400)
        )

        output = self._read(config_=config())
        # error was ignored and correct record was processed
        assert len(output.records) == 1
        assert output.records[0].record.data["page_id"]
        assert output.records[0].record.data["business_account_id"]
        assert output.records[0].record.data["id"]
        for metric in _METRICS:
            assert metric in output.records[0].record.data
