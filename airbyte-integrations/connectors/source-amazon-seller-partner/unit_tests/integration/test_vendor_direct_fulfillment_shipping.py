#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from http import HTTPStatus
from typing import List, Optional

import freezegun
import pendulum

from airbyte_cdk.models import AirbyteStateMessage, FailureType, SyncMode
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

from .config import NOW, TIME_FORMAT, ConfigBuilder
from .pagination import NEXT_TOKEN_STRING, VendorFulfillmentPaginationStrategy
from .request_builder import RequestBuilder
from .response_builder import response_with_status
from .utils import config, mock_auth, read_output


_START_DATE = pendulum.datetime(year=2023, month=1, day=1)
_END_DATE = pendulum.datetime(year=2023, month=1, day=5)
_REPLICATION_START_FIELD = "createdAfter"
_REPLICATION_END_FIELD = "createdBefore"
_CURSOR_FIELD = "createdBefore"
_STREAM_NAME = "VendorDirectFulfillmentShipping"


def _vendor_direct_fulfillment_shipping_request() -> RequestBuilder:
    return RequestBuilder.vendor_direct_fulfillment_shipping_endpoint().with_query_params(
        {
            _REPLICATION_START_FIELD: _START_DATE.strftime(TIME_FORMAT),
            _REPLICATION_END_FIELD: _END_DATE.strftime(TIME_FORMAT),
        }
    )


def _vendor_direct_fulfillment_shipping_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=NestedPath(["payload", "shippingLabels"]),
        pagination_strategy=VendorFulfillmentPaginationStrategy(),
    )


def _shipping_label_record() -> RecordBuilder:
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
            _vendor_direct_fulfillment_shipping_response().with_record(_shipping_label_record()).build(),
        )

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            _vendor_direct_fulfillment_shipping_response().with_pagination().with_record(_shipping_label_record()).build(),
        )
        query_params_with_next_page_token = {
            _REPLICATION_START_FIELD: _START_DATE.strftime(TIME_FORMAT),
            _REPLICATION_END_FIELD: _END_DATE.strftime(TIME_FORMAT),
            "nextToken": NEXT_TOKEN_STRING,
        }
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().with_query_params(query_params_with_next_page_token).build(),
            _vendor_direct_fulfillment_shipping_response()
            .with_record(_shipping_label_record())
            .with_record(_shipping_label_record())
            .build(),
        )

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE))
        assert len(output.records) == 3

    @HttpMocker()
    def test_given_two_slices_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        end_date = _START_DATE.add(days=8)
        mock_auth(http_mocker)

        query_params_first_slice = {
            _REPLICATION_START_FIELD: _START_DATE.strftime(TIME_FORMAT),
            _REPLICATION_END_FIELD: _START_DATE.add(days=6, hours=23, minutes=59, seconds=59).strftime(TIME_FORMAT),
        }
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().with_query_params(query_params_first_slice).build(),
            _vendor_direct_fulfillment_shipping_response().with_record(_shipping_label_record()).build(),
        )

        query_params_second_slice = {
            _REPLICATION_START_FIELD: _START_DATE.add(days=7).strftime(TIME_FORMAT),
            _REPLICATION_END_FIELD: end_date.strftime(TIME_FORMAT),
        }
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().with_query_params(query_params_second_slice).build(),
            _vendor_direct_fulfillment_shipping_response().with_record(_shipping_label_record()).build(),
        )

        output = self._read(config().with_start_date(_START_DATE).with_end_date(end_date))
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_http_status_500_then_200_when_read_then_retry_and_return_records(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            [
                response_with_status(status_code=HTTPStatus.INTERNAL_SERVER_ERROR),
                _vendor_direct_fulfillment_shipping_response().with_record(_shipping_label_record()).build(),
            ],
        )

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_http_status_500_on_availability_when_read_then_raise_system_error(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            response_with_status(status_code=HTTPStatus.INTERNAL_SERVER_ERROR),
        )

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error


@freezegun.freeze_time(NOW.isoformat())
class TestIncremental:
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
            _vendor_direct_fulfillment_shipping_response().with_record(_shipping_label_record()).build(),
        )

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE))
        expected_cursor_value = _END_DATE.strftime(TIME_FORMAT)
        assert output.records[0].record.data[_CURSOR_FIELD] == expected_cursor_value

    @HttpMocker()
    def test_when_read_then_state_message_produced_and_state_match_latest_record(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().build(),
            _vendor_direct_fulfillment_shipping_response()
            .with_record(_shipping_label_record())
            .with_record(_shipping_label_record())
            .build(),
        )

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE))
        assert len(output.state_messages) == 2

        cursor_value_from_latest_record = output.records[-1].record.data.get(_CURSOR_FIELD)

        most_recent_state = output.most_recent_state.stream_state
        assert most_recent_state.__dict__ == {_CURSOR_FIELD: cursor_value_from_latest_record}

    @HttpMocker()
    def test_given_state_when_read_then_state_value_is_created_after_query_param(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        state_value = _START_DATE.add(days=1).strftime(TIME_FORMAT)

        query_params_incremental_read = {_REPLICATION_START_FIELD: state_value, _REPLICATION_END_FIELD: _END_DATE.strftime(TIME_FORMAT)}

        http_mocker.get(
            _vendor_direct_fulfillment_shipping_request().with_query_params(query_params_incremental_read).build(),
            _vendor_direct_fulfillment_shipping_response()
            .with_record(_shipping_label_record())
            .with_record(_shipping_label_record())
            .build(),
        )

        output = self._read(
            config_=config().with_start_date(_START_DATE).with_end_date(_END_DATE),
            state=StateBuilder().with_stream_state(_STREAM_NAME, {_CURSOR_FIELD: state_value}).build(),
        )
        assert output.most_recent_state.stream_state.__dict__ == {_CURSOR_FIELD: _END_DATE.strftime(TIME_FORMAT)}
