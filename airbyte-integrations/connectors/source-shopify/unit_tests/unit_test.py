#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import requests
from source_shopify.source import BalanceTransactions, DiscountCodes, ShopifyStream, SourceShopify


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
    requests_mock.get(
        "https://test_shop.myshopify.com/admin/oauth/access_scopes.json",
        json={"access_scopes": [{"handle": "read_orders"}]},
    )
    source = SourceShopify()

    expected = [
        "abandoned_checkouts",
        "fulfillments",
        "metafield_orders",
        "metafield_shops",
        "order_refunds",
        "order_risks",
        "orders",
        "shop",
        "tender_transactions",
        "transactions",
    ]

    assert [stream.name for stream in source.streams(basic_config)] == expected


def test_unavailable_stream(requests_mock, basic_config):
    config = basic_config
    config["authenticator"] = None
    stream = BalanceTransactions(config)
    url = stream.url_base + stream.path()
    params = {"limit": 250, "order": stream.cursor_field + "+acs", "since_id": 0}
    requests_mock.get(url=url, json={"errors": "Not Found"}, status_code=404)
    response = requests.get(url, params)
    assert stream.should_retry(response) is False


def test_filter_records_newer_than_state(basic_config):
    config = basic_config
    config["authenticator"] = None
    stream = DiscountCodes(config)
    records_slice = [
        # present cursor older than state - record should be omitted
        {"id": 1, "updated_at": "2022-01-01T01:01:01-07:00"},
        # missing cursor, record should be present
        {"id": 2},
        # cursor is set to null
        {"id": 3, "updated_at": "null"},
        # cursor is set to null
        {"id": 4, "updated_at": None},
    ]
    state = {"updated_at": "2022-02-01T00:00:00-07:00"}

    # we expect records with: id = 2, 3, 4. We output them `As Is`,
    # because we cannot compare them to the STATE and SKIPPING them leads to data loss,
    expected = [{"id": 2}, {"id": 3, "updated_at": "null"}, {"id": 4, "updated_at": None}]
    result = list(stream.filter_records_newer_than_state(state, records_slice))
    assert result == expected
