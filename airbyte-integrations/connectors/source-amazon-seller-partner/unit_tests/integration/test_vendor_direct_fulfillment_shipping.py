#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import freezegun
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    NestedPath,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_protocol.models import SyncMode

from .config import NEXT_TOKEN_STRING, NOW, ConfigBuilder
from .pagination import VendorDirectFulfillmentShippingPaginationStrategy
from .request_builder import RequestBuilder
from .utils import config, mock_auth, read_output

_STREAM_NAME = "VendorDirectFulfillmentShipping"


def _vendor_direct_fulfillment_shipping_request() -> RequestBuilder:
    return RequestBuilder.vendor_direct_fulfillment_shipping_endpoint()


def _vendor_direct_fulfillment_shipping_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_STREAM_NAME, __file__),
        NestedPath(["payload", "shippingLabels"]),
        pagination_strategy=VendorDirectFulfillmentShippingPaginationStrategy(),
    )


def _a_shipping_label_record() -> RecordBuilder:
    return create_record_builder(
        find_template(_STREAM_NAME, __file__),
        NestedPath(["payload", "shippingLabels"]),
        record_id_path=FieldPath("purchaseOrderNumber"),
        # record_cursor_path=FieldPath("created"),
    )


@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh:

    @staticmethod
    def _read(stream_name: str, config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(config_, stream_name, SyncMode.full_refresh, expecting_exception=expecting_exception)

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            _vendor_direct_fulfillment_shipping_response().with_record(_a_shipping_label_record()).build(),
        )
        output = self._read(_STREAM_NAME, config())
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            _vendor_direct_fulfillment_shipping_response().with_pagination().with_record(_a_shipping_label_record()).build()
        )
        query_params_with_next_page_token = {"nextToken": NEXT_TOKEN_STRING}
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().with_query_params(query_params_with_next_page_token).build(),
            _vendor_direct_fulfillment_shipping_response().with_record(_a_shipping_label_record()).with_record(
                _a_shipping_label_record()
            ).build(),
        )
        output = self._read(_STREAM_NAME, config())
        assert len(output.records) == 3


class TestIncremental:

    @staticmethod
    def _read(stream_name: str, config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(config_, stream_name, SyncMode.incremental, expecting_exception=expecting_exception)

    @HttpMocker()
    def test_when_read_then_add_cursor_field(self, http_mocker: HttpMocker) -> None:
        cursor_field = "createdBefore"
        replication_start_date = NOW.subtract(days=3)
        replication_end_date = NOW
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            _vendor_direct_fulfillment_shipping_response().with_record(_a_shipping_label_record()).build()
        )

        output = self._read(_STREAM_NAME, config().with_start_date(replication_start_date).with_end_date(replication_end_date))

        expected_cursor_value = replication_end_date.isoformat()[:-13] + "Z"
        assert output.records[0].record.data[cursor_field] == expected_cursor_value
