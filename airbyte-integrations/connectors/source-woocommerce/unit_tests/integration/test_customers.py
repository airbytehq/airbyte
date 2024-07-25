# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

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

from .config import ConfigBuilder
from .request_builder import RequestBuilder, get_customers_request
from .utils import config, get_json_http_response, read_output

_CURSOR_FIELD = "id"
_STREAM_NAME = "customers"


def _get_request() -> RequestBuilder:
    return (
        RequestBuilder.get_customers_endpoint()
    )


def _get_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath('data'),
    )


def _record() -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath('data'),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath(_CURSOR_FIELD),
    )


class TestFullRefresh(TestCase):

    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(config_, _STREAM_NAME, SyncMode.full_refresh)

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            get_customers_request()
            .with_custom_param("orderby", "id")
            .with_custom_param("order", "asc")
            .with_custom_param("dates_are_gmt", "true")
            .with_custom_param("per_page", "100")
            .build(),
            get_json_http_response("customers.json",200),
        )

        output = self._read(config())

        assert len(output.records) == 2
