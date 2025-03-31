#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
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


_FIELDS = [
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

_CHILDREN_FIELDS = ["id", "ig_id", "media_type", "media_url", "owner", "permalink", "shortcode", "thumbnail_url", "timestamp", "username"]

_CHILDREN_IDS = ["07608776690540123", "52896800415362123", "39559889460059123", "17359925580923123"]
_STREAM_NAME = "media"


def _get_request() -> RequestBuilder:
    return RequestBuilder.get_media_endpoint(item_id=BUSINESS_ACCOUNT_ID).with_limit(100).with_fields(_FIELDS)


def _get_children_request(media_id: str) -> RequestBuilder:
    return RequestBuilder.get_media_children_endpoint(item_id=media_id).with_fields(_CHILDREN_FIELDS)


def _get_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath("data"),
        pagination_strategy=InstagramPaginationStrategy(request=_get_request().build(), next_page_token=NEXT_PAGE_TOKEN),
    )


def _record() -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(_STREAM_NAME, __file__),
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
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_request().build(),
            _get_response().with_record(_record()).build(),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_multiple_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_request().build(),
            _get_response().with_pagination().with_record(_record()).build(),
        )
        next_media_url = _get_request().with_next_page_token(NEXT_PAGE_TOKEN).build()
        http_mocker.get(
            next_media_url,
            _get_response().with_record(_record()).with_record(_record()).build(),
        )

        output = self._read(config_=config())
        assert len(output.records) == 3

    @HttpMocker()
    def test_when_read_then_datetime_fields_transformed(self, http_mocker: HttpMocker) -> None:
        created_time_field = "timestamp"
        input_datetime_value = "2024-01-01T00:00:00+0000"
        expected_datetime_value = "2024-01-01T00:00:00+00:00"
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(
            _get_request().build(),
            _get_response().with_record(_record().with_field(FieldPath(created_time_field), input_datetime_value)).build(),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data[created_time_field] == expected_datetime_value

    @HttpMocker()
    def test_given_one_page_has_children_field(self, http_mocker: HttpMocker) -> None:
        test = "children"
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        http_mocker.get(_get_request().build(), HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_for_{test}", __file__)), 200))

        for children_id in _CHILDREN_IDS:
            http_mocker.get(
                _get_children_request(children_id).build(),
                HttpResponse(json.dumps(find_template(f"{_STREAM_NAME}_children_for_{test}", __file__)), 200),
            )

        output = self._read(config_=config())
        assert len(output.records) == 1
        children = output.records[0].record.data["children"]
        assert len(children) == 4
        for child in children:
            assert "id" in child
            assert "ig_id" in child
            assert "media_type" in child
            assert "owner" in child
