#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest import TestCase

from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
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


FIELDS = [
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

_STREAM_NAME = "stories"


def _get_request() -> RequestBuilder:
    return RequestBuilder.get_stories_endpoint(item_id=BUSINESS_ACCOUNT_ID).with_limit(100).with_fields(FIELDS)


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
