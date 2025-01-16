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
from .request_builder import RequestBuilder, get_account_request
from .response_builder import get_account_response
from .utils import config, read_output


_CURSOR_FIELD = "id"

_STREAM_NAME = "user_lifetime_insights"


def _get_request() -> RequestBuilder:
    return (
        RequestBuilder.get_user_lifetime_insights_endpoint(item_id=BUSINESS_ACCOUNT_ID)
        .with_custom_param("metric", "follower_demographics")
        .with_custom_param("period", "lifetime")
        .with_custom_param("metric_type", "total_value")
        .with_limit(100)
    )


def _get_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath("data"),
    )


def _record() -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath(_CURSOR_FIELD),
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
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            get_account_request().build(),
            get_account_response(),
        )
        for breakdown in ["city", "country", "age,gender"]:
            lifetime_request = _get_request().with_custom_param("breakdown", breakdown)
            http_mocker.get(
                lifetime_request.build(),
                _get_response().with_record(_record()).build(),
            )

        output = self._read(config_=config())
        # each breakdown should produce a record
        assert len(output.records) == 3
