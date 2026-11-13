#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
import json
from unittest import TestCase

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
    "username",
]
_PARENT_STREAM_NAME = "stories"
_STREAM_NAME = "story_navigation_insights"

STORIES_ID = "3874523487643"
STORIES_ID_ERROR_CODE_10 = "3874523487644"

HAPPY_PATH = "story_navigation_insights_happy_path"
ERROR_10 = "story_navigation_insights_error_code_10"

_EXPECTED_METRICS = {
    "navigation": 25,
    "tap_forward": 19,
    "tap_back": 4,
    "tap_exit": 1,
    "swipe_forward": 1,
}


def _get_parent_request() -> RequestBuilder:
    return RequestBuilder.get_stories_endpoint(item_id=BUSINESS_ACCOUNT_ID).with_limit(100).with_fields(PARENT_FIELDS)


def _get_child_request(media_id: str) -> RequestBuilder:
    return (
        RequestBuilder.get_media_insights_endpoint(item_id=media_id)
        .with_custom_param("metric", "navigation")
        .with_custom_param("breakdown", "story_navigation_action_type")
    )


def _get_response(stream_name: str, test: str = None) -> HttpResponseBuilder:
    scenario = ""
    if test:
        scenario = f"_for_{test}"
    return create_response_builder(
        response_template=find_template(f"{stream_name}{scenario}", __file__),
        records_path=FieldPath("data"),
        pagination_strategy=InstagramPaginationStrategy(request=_get_parent_request().build(), next_page_token=NEXT_PAGE_TOKEN),
    )


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
    def test_instagram_story_navigation_insights(self, http_mocker: HttpMocker) -> None:
        test = HAPPY_PATH
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_parent_request().build(),
            _get_response(stream_name=_PARENT_STREAM_NAME, test=test).with_record(_record(stream_name=_PARENT_STREAM_NAME, test=test)).build(),
        )
        http_mocker.get(
            _get_child_request(media_id=STORIES_ID).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == STORIES_ID
        assert record["page_id"]
        assert record["business_account_id"]
        for metric, value in _EXPECTED_METRICS.items():
            assert record[metric] == value
        assert "data" not in record

    @HttpMocker()
    def test_instagram_story_navigation_insights_for_error_code_10(self, http_mocker: HttpMocker) -> None:
        """Test that error code 10 is gracefully ignored."""
        test = ERROR_10
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_parent_request().build(), HttpResponse(json.dumps(find_template(f"{_PARENT_STREAM_NAME}_for_{test}", __file__)), 200)
        )
        http_mocker.get(
            _get_child_request(media_id=STORIES_ID).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{HAPPY_PATH}", __file__)), 200),
        )
        http_mocker.get(
            _get_child_request(media_id=STORIES_ID_ERROR_CODE_10).build(),
            HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 400),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == STORIES_ID
        for metric, value in _EXPECTED_METRICS.items():
            assert output.records[0].record.data[metric] == value
        assert not any(log.log.level == "ERROR" for log in output.logs)
        log_messages = [log.log.message for log in output.logs]
        assert any("Insights error" in msg for msg in log_messages), f"Expected 'Insights error' in logs but got: {log_messages}"
