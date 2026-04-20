#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

import freezegun
import pendulum

from airbyte_cdk.models import SyncMode
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

from .config import MARKETPLACE_ID, NOW, TIME_FORMAT, ConfigBuilder
from .pagination import NEXT_TOKEN_STRING, FbaInboundPaginationStrategy
from .request_builder import RequestBuilder
from .utils import config, mock_auth, read_output


_START_DATE = pendulum.datetime(year=2023, month=1, day=1)
_END_DATE = pendulum.datetime(year=2023, month=1, day=5)


def _date_range_query_params() -> Mapping[str, Any]:
    return {
        "MarketplaceId": MARKETPLACE_ID,
        "QueryType": "DATE_RANGE",
        "LastUpdatedAfter": _START_DATE.strftime(TIME_FORMAT),
        "LastUpdatedBefore": _END_DATE.strftime(TIME_FORMAT),
    }


def _next_token_query_params() -> Mapping[str, Any]:
    # On paginated requests the connector must drop the date-range filters and
    # switch QueryType to NEXT_TOKEN, sending only MarketplaceId + QueryType + NextToken.
    return {
        "MarketplaceId": MARKETPLACE_ID,
        "QueryType": "NEXT_TOKEN",
        "NextToken": NEXT_TOKEN_STRING,
    }


@freezegun.freeze_time(NOW.isoformat())
class TestFbaInboundShipmentsFullRefresh:
    _STREAM_NAME = "FbaInboundShipments"
    _RECORDS_PATH = NestedPath(["payload", "ShipmentData"])

    def _request(self, query_params: Mapping[str, Any]) -> RequestBuilder:
        return RequestBuilder.fba_inbound_shipments_endpoint().with_query_params(query_params)

    def _response(self) -> HttpResponseBuilder:
        return create_response_builder(
            response_template=find_template(self._STREAM_NAME, __file__),
            records_path=self._RECORDS_PATH,
            pagination_strategy=FbaInboundPaginationStrategy(),
        )

    def _record(self) -> RecordBuilder:
        return create_record_builder(
            response_template=find_template(self._STREAM_NAME, __file__),
            records_path=self._RECORDS_PATH,
            record_id_path=FieldPath("ShipmentId"),
        )

    def _read(self, config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=self._STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            self._request(_date_range_query_params()).build(),
            self._response().with_record(self._record()).build(),
        )

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_then_only_marketplace_query_type_and_next_token_are_sent_on_paginated_request(
        self, http_mocker: HttpMocker
    ) -> None:
        """Regression test for the QueryType state machine: the SP-API rejects requests that combine
        QueryType=DATE_RANGE with NextToken. The first request must use QueryType=DATE_RANGE +
        LastUpdatedAfter/LastUpdatedBefore, and any paginated follow-up must use QueryType=NEXT_TOKEN +
        NextToken (no date filters).
        """
        mock_auth(http_mocker)
        http_mocker.get(
            self._request(_date_range_query_params()).build(),
            self._response().with_pagination().with_record(self._record()).build(),
        )
        http_mocker.get(
            self._request(_next_token_query_params()).build(),
            self._response().with_record(self._record()).with_record(self._record()).build(),
        )

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE))
        assert len(output.records) == 3


@freezegun.freeze_time(NOW.isoformat())
class TestFbaInboundShipmentItemsFullRefresh:
    _STREAM_NAME = "FbaInboundShipmentItems"
    _RECORDS_PATH = NestedPath(["payload", "ItemData"])

    def _request(self, query_params: Mapping[str, Any]) -> RequestBuilder:
        return RequestBuilder.fba_inbound_shipment_items_endpoint().with_query_params(query_params)

    def _response(self) -> HttpResponseBuilder:
        return create_response_builder(
            response_template=find_template(self._STREAM_NAME, __file__),
            records_path=self._RECORDS_PATH,
            pagination_strategy=FbaInboundPaginationStrategy(),
        )

    def _record(self) -> RecordBuilder:
        return create_record_builder(
            response_template=find_template(self._STREAM_NAME, __file__),
            records_path=self._RECORDS_PATH,
            record_id_path=FieldPath("SellerSKU"),
        )

    def _read(self, config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=self._STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            self._request(_date_range_query_params()).build(),
            self._response().with_record(self._record()).build(),
        )

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE))
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_then_only_marketplace_query_type_and_next_token_are_sent_on_paginated_request(
        self, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            self._request(_date_range_query_params()).build(),
            self._response().with_pagination().with_record(self._record()).build(),
        )
        http_mocker.get(
            self._request(_next_token_query_params()).build(),
            self._response().with_record(self._record()).with_record(self._record()).build(),
        )

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE))
        assert len(output.records) == 3
