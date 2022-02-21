#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import requests
from source_shopify.source import ShopifyStream, SourceShopify


def test_get_next_page_token(requests_mock):
    """
    Test shows that next_page parameters are parsed correctly from the response object and could be passed for next request API call,
    """
    response_header_links = {
        "Date": "Thu, 32 Jun 2099 24:24:24 GMT",
        "Content-Type": "application/json; charset=utf-8",
        "Link": '<https://test_shop.myshopify.com/admin/api/2021-04/test_object.json?limit=1&page_info=eyJjcmVhdGVkX2>; rel="next"',
    }
    expected_output_token = {
        "limit": "1",
        "page_info": "eyJjcmVhdGVkX2",
    }

    requests_mock.get("https://test.myshopify.com/", headers=response_header_links)
    response = requests.get("https://test.myshopify.com/")

    test = ShopifyStream.next_page_token(response)
    assert test == expected_output_token


def test_privileges_validation(requests_mock, basic_config):
    requests_mock.get("https://test_shop.myshopify.com/admin/oauth/access_scopes.json", json={"access_scopes": [{"handle": "read_orders"}]})
    source = SourceShopify()

    expected = [
        "customers",
        "orders",
        "draft_orders",
        "products",
        "abandoned_checkouts",
        "metafields",
        "custom_collections",
        "collects",
        "order_refunds",
        "order_risks",
        "transactions",
        "pages",
        "price_rules",
        "discount_codes",
        "locations",
        "inventory_items",
        "inventory_levels",
        "fulfillment_orders",
        "fulfillments",
        "shop",
    ]

    assert [stream.name for stream in source.streams(basic_config)] == expected
