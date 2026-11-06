#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from typing import Optional

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


_SHIPMENTS_STREAM_NAME = "FbaInboundShipments"
_ITEMS_STREAM_NAME = "FbaInboundShipmentItems"

_SHIPMENT_ID_1 = "FBA15D7ABCDE"
_SHIPMENT_ID_2 = "FBA15D7FGHIJ"

# `inbound_replication_mode` defaults to `rolling_days` with `inbound_rolling_days` defaulting to 30.
_DEFAULT_ROLLING_DAYS = 30

_SHIPMENT_STATUS_LIST = ",".join(
    [
        "WORKING",
        "READY_TO_SHIP",
        "SHIPPED",
        "RECEIVING",
        "CANCELLED",
        "DELETED",
        "CLOSED",
        "ERROR",
        "IN_TRANSIT",
        "DELIVERED",
        "CHECKED_IN",
    ]
)


def _shipments_request(
    last_updated_after: Optional[pendulum.DateTime] = None,
    last_updated_before: Optional[pendulum.DateTime] = None,
    next_token: Optional[str] = None,
) -> RequestBuilder:
    """
    getShipments expects `QueryType=DATE_RANGE` on the first request and `QueryType=NEXT_TOKEN` together with
    `NextToken` on every subsequent page.
    """
    query_params = {
        "MarketplaceId": MARKETPLACE_ID,
        "QueryType": "NEXT_TOKEN" if next_token else "DATE_RANGE",
        "ShipmentStatusList": _SHIPMENT_STATUS_LIST,
        "LastUpdatedAfter": (last_updated_after or NOW.subtract(days=_DEFAULT_ROLLING_DAYS)).strftime(TIME_FORMAT),
        "LastUpdatedBefore": (last_updated_before or NOW).strftime(TIME_FORMAT),
    }
    if next_token:
        query_params["NextToken"] = next_token
    return RequestBuilder.fba_inbound_shipments_endpoint().with_query_params(query_params)


def _shipments_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_SHIPMENTS_STREAM_NAME, __file__),
        records_path=NestedPath(["payload", "ShipmentData"]),
        pagination_strategy=FbaInboundPaginationStrategy(),
    )


def _shipment_record(shipment_id: str) -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(_SHIPMENTS_STREAM_NAME, __file__),
        records_path=NestedPath(["payload", "ShipmentData"]),
        record_id_path=FieldPath("ShipmentId"),
    ).with_id(shipment_id)


def _items_request(shipment_id: str) -> RequestBuilder:
    return RequestBuilder.fba_inbound_shipment_items_endpoint(shipment_id)


def _items_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_ITEMS_STREAM_NAME, __file__),
        records_path=NestedPath(["payload", "ItemData"]),
    )


def _item_record(seller_sku: str) -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(_ITEMS_STREAM_NAME, __file__),
        records_path=NestedPath(["payload", "ItemData"]),
        record_id_path=FieldPath("SellerSKU"),
    ).with_id(seller_sku)


@freezegun.freeze_time(NOW.isoformat())
class TestFbaInboundShipments:
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_SHIPMENTS_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(_shipments_request().build(), _shipments_response().with_record(_shipment_record(_SHIPMENT_ID_1)).build())

        output = self._read(config())

        assert len(output.records) == 1
        assert output.records[0].record.data["ShipmentId"] == _SHIPMENT_ID_1

    @HttpMocker()
    def test_given_two_pages_when_read_then_flip_query_type_and_return_all_records(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        # First page is a DATE_RANGE query and hands back `payload.NextToken`.
        http_mocker.get(
            _shipments_request().build(),
            _shipments_response().with_pagination().with_record(_shipment_record(_SHIPMENT_ID_1)).build(),
        )
        # Second page must switch to QueryType=NEXT_TOKEN and carry the token; no NextToken in the response ends the sync.
        http_mocker.get(
            _shipments_request(next_token=NEXT_TOKEN_STRING).build(),
            _shipments_response().with_record(_shipment_record(_SHIPMENT_ID_2)).build(),
        )

        output = self._read(config())

        assert len(output.records) == 2
        assert [record.record.data["ShipmentId"] for record in output.records] == [_SHIPMENT_ID_1, _SHIPMENT_ID_2]

    @HttpMocker()
    def test_given_rolling_days_when_read_then_window_ends_now(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _shipments_request(last_updated_after=NOW.subtract(days=7)).build(),
            _shipments_response().with_record(_shipment_record(_SHIPMENT_ID_1)).build(),
        )

        output = self._read(config().with_inbound_rolling_days(7))

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_fixed_replication_mode_when_read_then_use_configured_window(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        start_datetime = pendulum.datetime(year=2023, month=1, day=1)
        end_datetime = pendulum.datetime(year=2023, month=1, day=30)
        http_mocker.get(
            _shipments_request(last_updated_after=start_datetime, last_updated_before=end_datetime).build(),
            _shipments_response().with_record(_shipment_record(_SHIPMENT_ID_1)).build(),
        )

        output = self._read(config().with_inbound_fixed_window(start_datetime, end_datetime))

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_fixed_replication_mode_without_end_datetime_when_read_then_window_ends_now(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        start_datetime = pendulum.datetime(year=2023, month=1, day=1)
        http_mocker.get(
            _shipments_request(last_updated_after=start_datetime, last_updated_before=NOW).build(),
            _shipments_response().with_record(_shipment_record(_SHIPMENT_ID_1)).build(),
        )

        output = self._read(config().with_inbound_fixed_window(start_datetime))

        assert len(output.records) == 1


@freezegun.freeze_time(NOW.isoformat())
class TestFbaInboundShipmentItems:
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_ITEMS_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_given_two_parent_shipments_when_read_then_fetch_items_per_shipment(self, http_mocker: HttpMocker) -> None:
        mock_auth(http_mocker)
        http_mocker.get(
            _shipments_request().build(),
            _shipments_response().with_record(_shipment_record(_SHIPMENT_ID_1)).with_record(_shipment_record(_SHIPMENT_ID_2)).build(),
        )
        http_mocker.get(
            _items_request(_SHIPMENT_ID_1).build(),
            _items_response().with_record(_item_record("SKU-1-A")).with_record(_item_record("SKU-1-B")).build(),
        )
        http_mocker.get(
            _items_request(_SHIPMENT_ID_2).build(),
            _items_response().with_record(_item_record("SKU-2-A")).build(),
        )

        output = self._read(config())

        # `ShipmentId` is deliberately absent from the items response template, so it can only come from the
        # AddFields transformation reading `stream_slice['ShipmentId']`.
        assert len(output.records) == 3
        assert {(record.record.data["ShipmentId"], record.record.data["SellerSKU"]) for record in output.records} == {
            (_SHIPMENT_ID_1, "SKU-1-A"),
            (_SHIPMENT_ID_1, "SKU-1-B"),
            (_SHIPMENT_ID_2, "SKU-2-A"),
        }
