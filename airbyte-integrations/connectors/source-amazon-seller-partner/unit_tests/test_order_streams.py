#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest import mock

import pytest
import requests
from source_amazon_seller_partner.streams import OrderItems, Orders


@pytest.fixture
def orders_stream():
    def _internal(**kwargs):
        stream = Orders(
            url_base=kwargs.get("url_base", "https://test.url"),
            replication_start_date=kwargs.get("replication_start_date", "2023-08-08T00:00:00Z"),
            replication_end_date=kwargs.get("replication_end_date"),
            marketplace_id=kwargs.get("marketplace_id", "id"),
            authenticator=None,
            period_in_days=kwargs.get("period_in_days", 0),
            report_options=kwargs.get("report_options"),
        )
        return stream

    return _internal


@pytest.fixture
def order_items_stream():
    def _internal():
        stream = OrderItems(
            url_base="https://test.url",
            replication_start_date="2023-08-08T00:00:00Z",
            replication_end_date=None,
            marketplace_id="id",
            authenticator=None,
            period_in_days=0,
            report_options=None,
        )
        return stream

    return _internal


class TestOrders:
    def test_path(self, orders_stream):
        stream = orders_stream()
        assert stream.path() == "orders/v0/orders"

    @pytest.mark.parametrize(
        ("start_date", "end_date", "stream_state", "next_page_token", "expected_params"),
        (
            ("2022-09-01T00:00:00Z", "2022-10-01T00:00:00Z", {}, {"NextToken": "NextToken123"}, {"NextToken": "NextToken123"}),
            ("2022-09-01T00:00:00Z", None, {}, None, {"LastUpdatedAfter": "2022-09-01T00:00:00Z", "MaxResultsPerPage": 100}),
            (
                "2022-09-01T00:00:00Z",
                "2022-10-01T00:00:00Z",
                {},
                None,
                {"LastUpdatedAfter": "2022-09-01T00:00:00Z", "MaxResultsPerPage": 100, "LastUpdatedBefore": "2022-10-01T00:00:00Z"},
            ),
            (
                "2022-09-01T00:00:00Z",
                "2022-11-01T00:00:00Z",
                {"LastUpdateDate": "2022-10-01T00:00:00Z"},
                None,
                {"LastUpdatedAfter": "2022-10-01T00:00:00Z", "MaxResultsPerPage": 100, "LastUpdatedBefore": "2022-11-01T00:00:00Z"},
            ),
        ),
    )
    def test_request_params(self, orders_stream, start_date, end_date, stream_state, next_page_token, expected_params):
        marketplace_id = "market123"
        stream = orders_stream(replication_start_date=start_date, replication_end_date=end_date, marketplace_id=marketplace_id)
        expected_params.update({"MarketplaceIds": marketplace_id})
        assert stream.request_params(stream_state, next_page_token) == expected_params

    @pytest.mark.parametrize(
        ("response_headers", "expected_backoff_time"),
        (({"x-amzn-RateLimit-Limit": "2"}, 0.5), ({}, 60)),
    )
    def test_backoff_time(self, orders_stream, response_headers, expected_backoff_time):
        stream = orders_stream()
        response_mock = mock.MagicMock()
        response_mock.headers = response_headers
        assert stream.backoff_time(response_mock) == expected_backoff_time

    @pytest.mark.parametrize(
        ("payload", "expected_value"),
        (({"NextToken": "NextToken123"}, {"NextToken": "NextToken123"}), ({}, None)),
    )
    def test_next_page_token(self, mocker, orders_stream, payload, expected_value):
        stream = orders_stream()
        response_mock = requests.Response()
        mocker.patch.object(response_mock, "json", return_value={"payload": payload})
        assert stream.next_page_token(response_mock) == expected_value

    @pytest.mark.parametrize(
        ("current_stream_state", "latest_record", "expected_date"),
        (
            ({"LastUpdateDate": "2022-10-03T00:00:00Z"}, {"LastUpdateDate": "2022-10-04T00:00:00Z"}, "2022-10-04T00:00:00Z"),
            ({"LastUpdateDate": "2022-10-04T00:00:00Z"}, {"LastUpdateDate": "2022-10-03T00:00:00Z"}, "2022-10-04T00:00:00Z"),
            ({}, {"LastUpdateDate": "2022-10-03T00:00:00Z"}, "2022-10-03T00:00:00Z"),
        ),
    )
    def test_get_updated_state(self, orders_stream, current_stream_state, latest_record, expected_date):
        stream = orders_stream()
        expected_state = {stream.cursor_field: expected_date}
        assert stream._get_updated_state(current_stream_state, latest_record) == expected_state


class TestOrderItems:
    list_order_items_payload_data = {
        "payload": {
            "OrderItems": [
                {
                    "ProductInfo": {"NumberOfItems": "1"},
                    "IsGift": "false",
                    "BuyerInfo": {},
                    "QuantityShipped": 0,
                    "IsTransparency": False,
                    "QuantityOrdered": 1,
                    "ASIN": "AKDDKDKD",
                    "SellerSKU": "AAA-VPx3-AMZ",
                    "Title": "Example product",
                    "OrderItemId": "88888888888",
                }
            ],
            "AmazonOrderId": "111-0000000-2222222",
        }
    }

    def test_path(self, order_items_stream):
        stream = order_items_stream()
        stream_slice = {"AmazonOrderId": "AmazonOrderId123"}
        assert stream.path(stream_slice) == "orders/v0/orders/AmazonOrderId123/orderItems"

    @pytest.mark.parametrize(
        ("next_page_token", "expected_params"),
        (({"NextToken": "NextToken123"}, {"NextToken": "NextToken123"}), (None, {})),
    )
    def test_request_params(self, order_items_stream, next_page_token, expected_params):
        stream = order_items_stream()
        assert stream.request_params(stream_state={}, next_page_token=next_page_token) == expected_params

    @pytest.mark.parametrize(
        ("response_headers", "expected_backoff_time"),
        (({"x-amzn-RateLimit-Limit": "2"}, 0.5), ({}, 10)),
    )
    def test_backoff_time(self, order_items_stream, response_headers, expected_backoff_time):
        stream = order_items_stream()
        response_mock = mock.MagicMock()
        response_mock.headers = response_headers
        assert stream.backoff_time(response_mock) == expected_backoff_time

    def test_stream_initialization(self, order_items_stream):
        stream = order_items_stream()
        assert stream._replication_start_date == "2023-08-08T00:00:00Z"
        assert stream._replication_end_date is None
        assert stream.marketplace_id == "id"

    def test_stream_next_token(self, mocker, order_items_stream):
        response = requests.Response()
        token = "111111111"
        expected = {"NextToken": token}
        mocker.patch.object(response, "json", return_value={"payload": expected})
        assert expected == order_items_stream().next_page_token(response)

        mocker.patch.object(response, "json", return_value={"payload": {}})
        if order_items_stream().next_page_token(response) is not None:
            assert False

    def test_order_items_stream_parse_response(self, mocker, order_items_stream):
        response = requests.Response()
        mocker.patch.object(response, "json", return_value=self.list_order_items_payload_data)

        stream = order_items_stream()
        stream.cached_state["LastUpdateDate"] = "2023-08-07T00:00:00Z"
        parsed = stream.parse_response(
            response, stream_slice={"AmazonOrderId": "111-0000000-2222222", "LastUpdateDate": "2023-08-08T00:00:00Z"}
        )

        for record in parsed:
            assert record["AmazonOrderId"] == "111-0000000-2222222"
            assert record["OrderItemId"] == "88888888888"
            assert record["SellerSKU"] == "AAA-VPx3-AMZ"
            assert record["ASIN"] == "AKDDKDKD"
            assert record["Title"] == "Example product"
            assert record["QuantityOrdered"] == 1
            assert record["QuantityShipped"] == 0
            assert record["BuyerInfo"] == {}
            assert record["IsGift"] == "false"
            assert record["ProductInfo"] == {"NumberOfItems": "1"}

        assert stream.cached_state["LastUpdateDate"] == "2023-08-08T00:00:00Z"
