#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from http import HTTPStatus
from typing import List, Optional

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
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_protocol.models import AirbyteStateMessage, FailureType, SyncMode

from .config import NOW, ConfigBuilder
from .pagination import NEXT_TOKEN_STRING, VendorDirectFulfillmentShippingPaginationStrategy
from .request_builder import RequestBuilder
from .response_builder import response_with_status
from .utils import config, mock_auth, read_output

_STREAM_NAME = "VendorDirectFulfillmentShipping"
_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


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
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=NestedPath(["payload", "shippingLabels"]),
        record_id_path=FieldPath("purchaseOrderNumber"),
    )


@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh:

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
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            _vendor_direct_fulfillment_shipping_response().with_record(_a_shipping_label_record()).build(),
        )
        output = self._read(config())
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            _vendor_direct_fulfillment_shipping_response().with_pagination().with_record(
                _a_shipping_label_record()
            ).build(),
        )
        query_params_with_next_page_token = {"nextToken": NEXT_TOKEN_STRING}
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().with_query_params(query_params_with_next_page_token).build(),
            _vendor_direct_fulfillment_shipping_response().with_record(_a_shipping_label_record()).with_record(
                _a_shipping_label_record()
            ).build(),
        )
        output = self._read(config())
        assert len(output.records) == 3

    @HttpMocker()
    def test_given_http_status_500_then_200_when_read_then_retry_and_return_records(
        self, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            [
                response_with_status(status_code=HTTPStatus.INTERNAL_SERVER_ERROR),
                _vendor_direct_fulfillment_shipping_response().with_record(_a_shipping_label_record()).build(),
            ],
        )
        output = self._read(config())
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_on_availability_when_read_then_raise_system_error(
        self, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            response_with_status(status_code=HTTPStatus.INTERNAL_SERVER_ERROR),
        )
        output = self._read(config(), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.system_error


@freezegun.freeze_time(NOW.isoformat())
class TestIncremental:
    cursor_field = "createdBefore"
    replication_start_date = NOW.subtract(days=3)
    replication_end_date = NOW

    @staticmethod
    def _read(
        config_: ConfigBuilder, state: Optional[List[AirbyteStateMessage]] = None, expecting_exception: bool = False
    ) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.incremental,
            state=state,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_when_read_then_add_cursor_field(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            _vendor_direct_fulfillment_shipping_response().with_record(_a_shipping_label_record()).build(),
        )

        output = self._read(
            config().with_start_date(self.replication_start_date).with_end_date(self.replication_end_date)
        )

        expected_cursor_value = self.replication_end_date.strftime(_TIME_FORMAT)
        assert output.records[0].record.data[self.cursor_field] == expected_cursor_value

    @HttpMocker()
    def test_when_read_then_state_message_produced_and_state_match_latest_record(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            _vendor_direct_fulfillment_shipping_response().with_record(_a_shipping_label_record()).with_record(
                _a_shipping_label_record()
            ).build(),
        )

        output = self._read(
            config().with_start_date(self.replication_start_date).with_end_date(self.replication_end_date)
        )
        assert len(output.state_messages) == 1

        cursor_value_from_state_message = output.most_recent_state.get(_STREAM_NAME, {}).get(self.cursor_field)
        cursor_value_from_latest_record = output.records[-1].record.data.get(self.cursor_field)
        assert cursor_value_from_state_message == cursor_value_from_latest_record

    @HttpMocker()
    def test_given_state_when_read_then_state_value_is_created_after_query_param(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        state_value = self.replication_start_date.add(days=1).strftime(_TIME_FORMAT)

        query_params_first_read = {
            "createdAfter": self.replication_start_date.strftime(_TIME_FORMAT),
            self.cursor_field: self.replication_end_date.strftime(_TIME_FORMAT),
        }
        query_params_incremental_read = {
            "createdAfter": state_value, self.cursor_field: self.replication_end_date.strftime(_TIME_FORMAT)
        }

        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().with_query_params(query_params_first_read).build(),
            _vendor_direct_fulfillment_shipping_response().with_record(_a_shipping_label_record()).with_record(
                _a_shipping_label_record()
            ).build(),
        )
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().with_query_params(query_params_incremental_read).build(),
            _vendor_direct_fulfillment_shipping_response().with_record(_a_shipping_label_record()).with_record(
                _a_shipping_label_record()
            ).build(),
        )
        output = self._read(
            config_=config().with_start_date(self.replication_start_date).with_end_date(self.replication_end_date),
            state=StateBuilder().with_stream_state(_STREAM_NAME, {self.cursor_field: state_value}).build(),
        )
        assert output.most_recent_state == {
            _STREAM_NAME: {self.cursor_field: self.replication_end_date.strftime(_TIME_FORMAT)}
        }
