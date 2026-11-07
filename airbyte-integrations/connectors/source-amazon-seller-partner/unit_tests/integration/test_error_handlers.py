#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from http import HTTPStatus

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import NOW
from .request_builder import RequestBuilder
from .response_builder import build_response, response_with_status
from .utils import assert_no_rate_limited_status, config, mock_auth, read_output


_ORDER_ID = "order-123"
_SHIPMENT_ID = "shipment-123"
_ERROR_HANDLER_CASES = (
    ("Orders", "orders/v0/orders", "Orders", None, None),
    (
        "OrderItems",
        f"orders/v0/orders/{_ORDER_ID}/orderItems",
        "OrderItems",
        "orders/v0/orders",
        "Orders",
    ),
    (
        "VendorDirectFulfillmentShipping",
        "vendor/directFulfillment/shipping/v1/shippingLabels",
        "shippingLabels",
        None,
        None,
    ),
    ("VendorOrders", "vendor/orders/v1/purchaseOrders", "orders", None, None),
    ("VendorOrdersStatus", "vendor/orders/v1/purchaseOrdersStatus", "ordersStatus", None, None),
    ("FbaInboundShipments", "fba/inbound/v0/shipments", "ShipmentData", None, None),
    (
        "FbaInboundShipmentItems",
        f"fba/inbound/v0/shipments/{_SHIPMENT_ID}/items",
        "ItemData",
        "fba/inbound/v0/shipments",
        "ShipmentData",
    ),
    ("ListFinancialEventGroups", "finances/v0/financialEventGroups", "FinancialEventGroupList", None, None),
)


def _payload_response(records_key: str, record: dict) -> HttpResponse:
    return build_response({"payload": {records_key: [record]}}, status_code=HTTPStatus.OK)


def _parent_response(stream_name: str) -> HttpResponse:
    if stream_name == "OrderItems":
        return _payload_response(
            "Orders",
            {"AmazonOrderId": _ORDER_ID, "LastUpdateDate": "2023-01-05T00:00:00Z"},
        )
    return _payload_response("ShipmentData", {"ShipmentId": _SHIPMENT_ID})


@freezegun.freeze_time(NOW.isoformat())
@pytest.mark.parametrize(
    ("stream_name", "endpoint", "records_key", "parent_endpoint", "parent_records_key"),
    _ERROR_HANDLER_CASES,
)
@HttpMocker()
def test_given_forbidden_once_when_read_then_retried_and_records_emitted(
    stream_name: str,
    endpoint: str,
    records_key: str,
    parent_endpoint: str | None,
    parent_records_key: str | None,
    http_mocker: HttpMocker,
) -> None:
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    if parent_endpoint and parent_records_key:
        http_mocker.get(
            RequestBuilder(parent_endpoint).build(),
            _parent_response(stream_name),
        )

    request = RequestBuilder(endpoint).build()
    http_mocker.get(
        request,
        [
            response_with_status(status_code=HTTPStatus.FORBIDDEN),
            _payload_response(records_key, {"id": "record-1"}),
        ],
    )

    config_builder = config().with_end_date(datetime(2023, 1, 7))
    if stream_name.startswith("Vendor"):
        config_builder.with_account_type("Vendor")
    output = read_output(
        config_builder=config_builder,
        stream_name=stream_name,
        sync_mode=SyncMode.full_refresh,
    )

    assert len(output.errors) == 0
    assert len(output.records) == 1
    http_mocker.assert_number_of_calls(request, 2)


@freezegun.freeze_time(NOW.isoformat())
@pytest.mark.parametrize(
    ("stream_name", "endpoint", "records_key", "parent_endpoint"),
    [
        ("FbaInboundShipments", "fba/inbound/v0/shipments", "ShipmentData", None),
        (
            "FbaInboundShipmentItems",
            f"fba/inbound/v0/shipments/{_SHIPMENT_ID}/items",
            "ItemData",
            "fba/inbound/v0/shipments",
        ),
    ],
)
@HttpMocker()
def test_given_throttled_once_when_read_then_retried_without_rate_limited_status(
    stream_name: str,
    endpoint: str,
    records_key: str,
    parent_endpoint: str | None,
    http_mocker: HttpMocker,
    capsys: pytest.CaptureFixture[str],
) -> None:
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    if parent_endpoint:
        http_mocker.get(
            RequestBuilder(parent_endpoint).build(),
            _parent_response(stream_name),
        )

    request = RequestBuilder(endpoint).build()
    http_mocker.get(
        request,
        [
            response_with_status(status_code=HTTPStatus.TOO_MANY_REQUESTS),
            _payload_response(records_key, {"id": "record-1"}),
        ],
    )

    output = read_output(
        config_builder=config(),
        stream_name=stream_name,
        sync_mode=SyncMode.full_refresh,
    )
    assert len(output.errors) == 0
    assert len(output.records) == 1
    assert_no_rate_limited_status(capsys.readouterr().out)
    http_mocker.assert_number_of_calls(request, 2)


@freezegun.freeze_time(NOW.isoformat())
@HttpMocker()
def test_given_invalid_financial_event_input_when_read_then_fails_with_configuration_guidance(
    http_mocker: HttpMocker,
) -> None:
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(
        RequestBuilder("finances/v0/financialEvents").build(),
        response_with_status(
            status_code=HTTPStatus.BAD_REQUEST,
            body={"errors": [{"code": "InvalidInput", "message": "Too many transactions"}]},
        ),
    )

    output = read_output(
        config_builder=config(),
        stream_name="ListFinancialEvents",
        sync_mode=SyncMode.incremental,
    )

    assert output.errors
    assert "lower the 'Financial Events Max Results Per Page'" in output.errors[0].trace.error.message
