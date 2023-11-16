#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from source_amazon_seller_partner.streams import OrderItems

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
            advanced_stream_options=None,
            max_wait_seconds=500,
        )
        return stream

    return _internal


def test_order_items_stream_initialization(order_items_stream):
    stream = order_items_stream()
    assert stream._replication_start_date == "2023-08-08T00:00:00Z"
    assert stream._replication_end_date is None
    assert stream.marketplace_id == "id"


def test_order_items_stream_next_token(mocker, order_items_stream):
    response = requests.Response()
    token = "111111111"
    expected = {"NextToken": token}
    mocker.patch.object(response, "json", return_value={"payload": expected})
    assert expected == order_items_stream().next_page_token(response)

    mocker.patch.object(response, "json", return_value={"payload": {}})
    if order_items_stream().next_page_token(response) is not None:
        assert False


def test_order_items_stream_parse_response(mocker, order_items_stream):
    response = requests.Response()
    mocker.patch.object(response, "json", return_value=list_order_items_payload_data)

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
