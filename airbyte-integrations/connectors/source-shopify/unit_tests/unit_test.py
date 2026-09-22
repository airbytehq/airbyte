#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Mapping, Optional
from unittest.mock import patch

import pytest
import requests
from source_shopify.run import run
from source_shopify.source import ConnectionCheckTest, SourceShopify
from source_shopify.streams.streams import BalanceTransactions, Countries, DiscountCodes, MarketCountries, PriceRules
from source_shopify.utils import ShopifyNonRetryableErrors


def test_get_next_page_token(requests_mock, auth_config):
    """
    Test shows that next_page parameters are parsed correctly from the response object and could be passed for next request API call,
    """
    stream = PriceRules(auth_config)
    response_header_links = {
        "Date": "Thu, 32 Jun 2099 24:24:24 GMT",
        "Content-Type": "application/json; charset=utf-8",
        "Link": '<https://test-shop.myshopify.com/admin/api/2021-04/test_object.json?limit=1&page_info=eyJjcmVhdGVkX2>; rel="next"',
    }
    expected_output_token = {
        "limit": "1",
        "page_info": "eyJjcmVhdGVkX2",
    }

    requests_mock.get("https://test.myshopify.com/", headers=response_header_links)
    response = requests.get("https://test.myshopify.com/")

    test = stream.next_page_token(response=response)
    assert test == expected_output_token


@pytest.mark.parametrize(
    "fetch_transactions_user_id, expected",
    [
        (
            True,
            [
                "abandoned_checkouts",
                "customer_journey_summary",
                "fulfillments",
                "metafield_orders",
                "metafield_shops",
                "order_agreements",
                "order_refunds",
                "order_risks",
                "orders",
                "shop",
                "tender_transactions",
                "transactions",
            ],
        ),
        (
            False,
            [
                "abandoned_checkouts",
                "customer_journey_summary",
                "fulfillments",
                "metafield_orders",
                "metafield_shops",
                "order_agreements",
                "order_refunds",
                "order_risks",
                "orders",
                "shop",
                "tender_transactions",
                "transactions",
            ],
        ),
    ],
)
def test_privileges_validation(requests_mock, fetch_transactions_user_id, basic_config, expected):
    requests_mock.get(
        "https://test-shop.myshopify.com/admin/oauth/access_scopes.json",
        json={"access_scopes": [{"handle": "read_orders"}]},
    )
    basic_config["fetch_transactions_user_id"] = fetch_transactions_user_id
    # mock the get_shop_id method
    with patch.object(ConnectionCheckTest, "get_shop_id", return_value=123) as mock:
        source = SourceShopify()
        streams = source.streams(basic_config)
    assert [stream.name for stream in streams] == expected


@pytest.mark.parametrize(
    "stream, slice, status_code, json_response",
    [(BalanceTransactions, None, 404, {"errors": "Not Found"}), (PriceRules, None, 403, {"errors": "Forbidden"})],
    ids=["Stream not found (404)", "No permissions (403)"],
)
def test_unavailable_stream(
    requests_mock, auth_config, stream, slice: Optional[Mapping[str, Any]], status_code: int, json_response: Mapping[str, Any]
):
    stream = stream(auth_config)
    url = stream.url_base + stream.path(stream_slice=slice)
    requests_mock.get(url=url, json=json_response, status_code=status_code)
    response = requests.get(url)
    expected_error_resolution = ShopifyNonRetryableErrors(stream.name).get(status_code)
    assert stream.get_error_handler().interpret_response(response) == expected_error_resolution


def test_filter_records_newer_than_state(auth_config):
    stream = DiscountCodes(auth_config)
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


def test_run_module_emits_spec():
    with patch("sys.argv", ["", "spec"]):
        # dummy test for the spec
        assert run() is None


@pytest.mark.parametrize(
    "parent_slices, expected_slices",
    [
        pytest.param(
            [{"parent": {"profile_location_groups": [{"locationGroup": {"id": "123"}}]}}],
            [{"parent": {"profile_location_groups": [{"locationGroup": {"id": "123"}}]}}],
            id="slice_with_non_empty_profile_location_groups_is_kept",
        ),
        pytest.param(
            [{"parent": {"profile_location_groups": []}}],
            [],
            id="slice_with_empty_profile_location_groups_is_filtered",
        ),
        pytest.param(
            [{"parent": {}}],
            [],
            id="slice_with_missing_profile_location_groups_is_filtered",
        ),
        pytest.param(
            [
                {"parent": {"profile_location_groups": [{"locationGroup": {"id": "123"}}]}},
                {"parent": {"profile_location_groups": []}},
                {"parent": {"profile_location_groups": [{"locationGroup": {"id": "456"}}]}},
            ],
            [
                {"parent": {"profile_location_groups": [{"locationGroup": {"id": "123"}}]}},
                {"parent": {"profile_location_groups": [{"locationGroup": {"id": "456"}}]}},
            ],
            id="mixed_slices_filters_only_empty_profile_location_groups",
        ),
    ],
)
def test_countries_stream_slices_filters_empty_profile_location_groups(mocker, requests_mock, auth_config, parent_slices, expected_slices):
    """
    Test that Countries.stream_slices filters out slices where profile_location_groups is empty.
    This prevents IndexError when request_body_json tries to access profile_location_groups[0].
    """
    mock_shop_features(requests_mock, market_driven_shipping=False)
    mocker.patch(
        "source_shopify.streams.streams.HttpSubStream.stream_slices",
        return_value=iter(parent_slices),
    )
    stream = Countries(parent=mocker.MagicMock(), config=auth_config)
    result = list(stream.stream_slices())
    assert result == expected_slices


def mock_shop_features(requests_mock, market_driven_shipping: bool) -> None:
    requests_mock.post(
        "https://test-shop.myshopify.com/admin/api/2026-07/graphql.json",
        json={"data": {"shop": {"features": {"marketDrivenShipping": market_driven_shipping}}}},
    )


@pytest.mark.parametrize(
    "market_driven_shipping, expected_slices",
    [
        pytest.param(
            False, [{"parent": {"profile_location_groups": [{"locationGroup": {"id": "123"}}]}}], id="legacy_shop_reads_delivery_profiles"
        ),
        pytest.param(True, [], id="market_driven_shop_emits_nothing"),
    ],
)
def test_countries_stream_slices_gated_by_market_driven_shipping(
    mocker, requests_mock, auth_config, market_driven_shipping, expected_slices
):
    mock_shop_features(requests_mock, market_driven_shipping)
    parent_slices = mocker.patch(
        "source_shopify.streams.streams.HttpSubStream.stream_slices",
        return_value=iter([{"parent": {"profile_location_groups": [{"locationGroup": {"id": "123"}}]}}]),
    )
    stream = Countries(parent=mocker.MagicMock(), config=auth_config)
    assert list(stream.stream_slices()) == expected_slices
    # the parent `deliveryProfiles` stream is not read at all for market-driven shops
    assert parent_slices.called is not market_driven_shipping


@pytest.mark.parametrize(
    "market_driven_shipping, expected_slices",
    [
        pytest.param(False, [], id="legacy_shop_emits_nothing"),
        pytest.param(True, [{}], id="market_driven_shop_reads_markets"),
    ],
)
def test_market_countries_stream_slices_gated_by_market_driven_shipping(
    requests_mock, auth_config, market_driven_shipping, expected_slices
):
    mock_shop_features(requests_mock, market_driven_shipping)
    stream = MarketCountries(auth_config)
    assert list(stream.stream_slices()) == expected_slices


def test_market_driven_shipping_flag_is_fetched_once_and_defaults_to_false(requests_mock, auth_config):
    requests_mock.post("https://test-shop.myshopify.com/admin/api/2026-07/graphql.json", json={"data": {"shop": {"features": {}}}})
    stream = MarketCountries(auth_config)
    assert stream.market_driven_shipping_enabled is False
    assert stream.market_driven_shipping_enabled is False
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json() == {
        "query": "query ShopFeatures {\n  shop {\n    features {\n      marketDrivenShipping\n    }\n  }\n}"
    }


def test_market_driven_shipping_flag_warns_on_graphql_error(requests_mock, auth_config, caplog):
    requests_mock.post(
        "https://test-shop.myshopify.com/admin/api/2026-07/graphql.json",
        json={"errors": [{"message": "Field 'marketDrivenShipping' doesn't exist on type 'ShopFeatures'"}]},
    )
    stream = MarketCountries(auth_config)
    with caplog.at_level(logging.WARNING, logger="airbyte"):
        assert stream.market_driven_shipping_enabled is False
    assert "could not read `shop.features.marketDrivenShipping`" in caplog.text
    assert "Field 'marketDrivenShipping' doesn't exist" in caplog.text
