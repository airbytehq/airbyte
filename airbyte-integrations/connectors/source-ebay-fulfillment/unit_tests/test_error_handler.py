# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for eBay Fulfillment stream error handling."""

import json
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_STREAM_NAME = "orders"
_REFRESH_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
_API_BASE_URL = "https://api.ebay.com"
_CONFIG = {
    "refresh_token_endpoint": _REFRESH_TOKEN_URL,
    "api_host": _API_BASE_URL,
    "username": "test-username",
    "password": "test-password",
    "redirect_uri": "test-redirect-uri",
    "refresh_token": "test-refresh-token",
    "start_date": "2024-01-01T00:00:00Z",
}
_TOKEN_REQUEST = HttpRequest(
    url=_REFRESH_TOKEN_URL,
    body="grant_type=refresh_token&redirect_uri=test-redirect-uri&refresh_token=test-refresh-token",
)
_ORDERS_REQUEST = HttpRequest(
    url=f"{_API_BASE_URL}/sell/fulfillment/v1/order",
    query_params={
        "offset": "0",
        "limit": "200",
        "filter": "lastmodifieddate:[2024-01-01T00:00:00.000000Z..]",
    },
)


def _order(order_id: str) -> Dict[str, Any]:
    return {"orderId": order_id}


def _orders_response(*orders: Dict[str, Any], status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps({"orders": list(orders)}), status_code=status_code)


def _mock_token(http_mocker: HttpMocker) -> None:
    http_mocker.post(_TOKEN_REQUEST, HttpResponse(json.dumps({"access_token": "test-token"})))


def _read_orders(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(
        get_source(config=_CONFIG),
        _CONFIG,
        catalog,
        expecting_exception=expecting_exception,
    )


def test_orders_uses_default_error_handler() -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())

    assert manifest["definitions"]["streams"]["orders"]["retriever"]["requester"]["error_handler"] == {"type": "DefaultErrorHandler"}


def test_manifest_does_not_use_composite_error_handler() -> None:
    assert "".join(("Composite", "ErrorHandler")) not in _YAML_FILE_PATH.read_text()


@patch("time.sleep", lambda _: None)
class TestOrdersErrorHandler(TestCase):
    @HttpMocker()
    def test_orders_records_are_emitted(self, http_mocker: HttpMocker) -> None:
        _mock_token(http_mocker)
        http_mocker.get(_ORDERS_REQUEST, _orders_response(_order("order-1")))

        output = _read_orders()

        assert [record.record.data["orderId"] for record in output.records] == ["order-1"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_ORDERS_REQUEST, 1)

    @HttpMocker()
    def test_429_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        _mock_token(http_mocker)
        http_mocker.get(
            _ORDERS_REQUEST,
            [
                HttpResponse(body="", status_code=429),
                _orders_response(_order("order-1")),
            ],
        )

        output = _read_orders()

        assert [record.record.data["orderId"] for record in output.records] == ["order-1"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_ORDERS_REQUEST, 2)

    @HttpMocker()
    def test_500_is_retried_then_succeeds(self, http_mocker: HttpMocker) -> None:
        _mock_token(http_mocker)
        http_mocker.get(
            _ORDERS_REQUEST,
            [
                HttpResponse(body="", status_code=500),
                _orders_response(_order("order-1")),
            ],
        )

        output = _read_orders()

        assert [record.record.data["orderId"] for record in output.records] == ["order-1"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_ORDERS_REQUEST, 2)

    @HttpMocker()
    def test_403_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        _mock_token(http_mocker)
        http_mocker.get(_ORDERS_REQUEST, HttpResponse(body="", status_code=403))

        output = _read_orders(expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_ORDERS_REQUEST, 1)
