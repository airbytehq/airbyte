#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import logging
import math
import re
from unittest.mock import MagicMock, patch

import jsonschema
import pytest
import requests
from source_shopify.auth import ShopifyAuthenticator
from source_shopify.source import ConnectionCheckTest, ShopifyScopes, SourceShopify
from source_shopify.streams.streams import (
    AbandonedCheckouts,
    Articles,
    Blogs,
    Collects,
    Countries,
    CustomCollections,
    Customers,
    DiscountCodes,
    DraftOrders,
    FulfillmentOrders,
    Fulfillments,
    InventoryLevels,
    Locations,
    MarketCountries,
    MetafieldArticles,
    MetafieldBlogs,
    MetafieldCollections,
    MetafieldCustomers,
    MetafieldDraftOrders,
    MetafieldLocations,
    MetafieldOrders,
    MetafieldPages,
    MetafieldProducts,
    MetafieldProductVariants,
    MetafieldShops,
    MetafieldSmartCollections,
    OrderRefunds,
    OrderRisks,
    Orders,
    Pages,
    PriceRules,
    ProductImages,
    Products,
    ProductVariants,
    Shop,
    TenderTransactions,
    Transactions,
    TransactionsGraphql,
)
from source_shopify.utils import ShopifyWrongShopNameError

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteStream, DestinationSyncMode, FailureType, SyncMode
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger
from airbyte_cdk.utils import AirbyteTracedException

from .conftest import records_per_slice


@pytest.fixture
def config(basic_config) -> dict:
    basic_config["start_date"] = "2020-11-01"
    basic_config["authenticator"] = ShopifyAuthenticator(basic_config)
    return basic_config


@pytest.mark.parametrize(
    "stream,stream_slice,expected_path",
    [
        (Articles, None, "articles.json"),
        (Blogs, None, "blogs.json"),
        (MetafieldBlogs, {"id": 123}, "blogs/123/metafields.json"),
        (MetafieldArticles, {"id": 123}, "articles/123/metafields.json"),
        # GraphQL Bulk Streams
        (MetafieldCustomers, None, "graphql.json"),
        (MetafieldOrders, None, "graphql.json"),
        (MetafieldDraftOrders, None, "graphql.json"),
        (MetafieldProducts, None, "graphql.json"),
        (MetafieldProductVariants, None, "graphql.json"),
        (MetafieldLocations, None, "graphql.json"),
        (MetafieldCollections, None, "graphql.json"),
        (Products, None, "graphql.json"),
        (ProductImages, None, "graphql.json"),
        (ProductVariants, None, "graphql.json"),
        # Nested Substreams
        (OrderRefunds, None, ""),
        # regular streams
        (MetafieldSmartCollections, {"id": 123}, "smart_collections/123/metafields.json"),
        (MetafieldPages, {"id": 123}, "pages/123/metafields.json"),
        (MetafieldShops, None, "metafields.json"),
        (Customers, None, "customers.json"),
        (Orders, None, "orders.json"),
        (DraftOrders, None, "draft_orders.json"),
        (AbandonedCheckouts, None, "checkouts.json"),
        (Collects, None, "collects.json"),
        (TenderTransactions, None, "tender_transactions.json"),
        (Pages, None, "pages.json"),
        (PriceRules, None, "price_rules.json"),
        (Locations, None, "locations.json"),
        (Shop, None, "shop.json"),
        (CustomCollections, None, "custom_collections.json"),
    ],
)
def test_path(stream, stream_slice, expected_path, config) -> None:
    stream = stream(config)
    if stream_slice:
        result = stream.path(stream_slice)
    else:
        result = stream.path()
    assert result == expected_path


@pytest.mark.parametrize(
    "stream,stream_slice,expected_path",
    [
        (Transactions, {"order_id": 12345}, "orders/12345/transactions.json"),
        # Nested Substreams
        (OrderRefunds, None, ""),
        (Fulfillments, None, ""),
        # GQL BULK stream
        (OrderRisks, None, "graphql.json"),
        (DiscountCodes, None, "graphql.json"),
        (FulfillmentOrders, None, "graphql.json"),
        (InventoryLevels, None, "graphql.json"),
    ],
)
def test_path_with_stream_slice_param(stream, stream_slice, expected_path, config) -> None:
    stream = stream(config)
    if stream_slice:
        result = stream.path(stream_slice)
    else:
        result = stream.path()
    assert result == expected_path


@pytest.mark.parametrize(
    "stream, parent_records, state_checkpoint_interval",
    [
        (
            OrderRefunds,
            [
                {"id": 1, "refunds": [{"created_at": "2021-01-01T00:00:00+00:00"}]},
                {"id": 2, "refunds": [{"created_at": "2021-02-01T00:00:00+00:00"}]},
                {"id": 3, "refunds": [{"created_at": "2021-03-01T00:00:00+00:00"}]},
                {"id": 4, "refunds": [{"created_at": "2021-04-01T00:00:00+00:00"}]},
                {"id": 5, "refunds": [{"created_at": "2021-05-01T00:00:00+00:00"}]},
            ],
            2,
        ),
    ],
)
def test_stream_slice_nested_substream_buffering(
    mocker,
    config,
    stream,
    parent_records,
    state_checkpoint_interval,
) -> None:
    # making the stream instance
    stream = stream(config)
    stream.state_checkpoint_interval = state_checkpoint_interval
    # simulating `read_records` for the `parent_stream`
    mocker.patch(
        "source_shopify.streams.base_streams.IncrementalShopifyStreamWithDeletedEvents.read_records",
        return_value=parent_records,
    )
    # count how many slices we expect, based on the number of parent_records
    total_slices_expected = math.ceil(len(parent_records) / state_checkpoint_interval)
    # define the how many records each individual slice should have, based on the number of parent_records
    expected_records_per_slice = records_per_slice(parent_records, state_checkpoint_interval)
    # slices counter
    total_slices: int = 0
    for slice in enumerate(stream.stream_slices()):
        slice_index = slice[0]
        nested_records = slice[1].get(stream.nested_entity)
        # check the number of records / slice
        assert len(nested_records) == expected_records_per_slice[slice_index]
        # count total slices
        total_slices += 1
    # check we have emitted complete number of slices
    assert total_slices == total_slices_expected


def test_check_connection(config, mocker) -> None:
    mocker.patch("source_shopify.streams.streams.Shop.read_records", return_value=[{"id": 1}])
    source = SourceShopify()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_check_connection_invalid_shop_returns_clear_error(config) -> None:
    # A malformed `shop` must surface a clear, actionable reason at check time rather than
    # letting ShopifyWrongShopNameError escape to the generic top-level handler.
    config["shop"] = "https://test-store.myshopify.com/admin"
    source = SourceShopify()
    logger_mock = MagicMock()
    succeeded, message = source.check_connection(logger_mock, config)
    assert succeeded is False
    assert "Shopify Store" in message
    assert "https://test-store.myshopify.com/admin" in message


def test_read_records(config, mocker) -> None:
    records = [{"created_at": "2022-10-10T06:21:53-07:00", "orders": {"updated_at": "2022-10-10T06:21:53-07:00"}}]
    stream_slice = records[0]
    stream = OrderRefunds(config)
    mocker.patch("source_shopify.streams.base_streams.IncrementalShopifyNestedStream.read_records", return_value=records)
    assert stream.read_records(stream_slice=stream_slice)[0] == records[0]


@pytest.mark.parametrize(
    "stream, expected",
    [
        # Nested Substream
        (OrderRefunds, {}),
        #
        (Orders, {"limit": 250, "status": "any", "order": "updated_at asc", "updated_at_min": "2020-11-01"}),
        (
            AbandonedCheckouts,
            {"limit": 250, "status": "any", "order": "updated_at asc", "updated_at_min": "2020-11-01"},
        ),
    ],
)
def test_request_params(config, stream, expected) -> None:
    assert stream(config).request_params() == expected


@pytest.mark.parametrize(
    "last_record, current_state, expected",
    [
        # no init state
        (
            {"created_at": "2022-10-10T06:21:53-07:00"},
            {},
            {"created_at": "2022-10-10T06:21:53-07:00", "orders": {"updated_at": "", "deleted": {"deleted_at": ""}}},
        ),
        # state is empty str
        (
            {"created_at": "2022-10-10T06:21:53-07:00"},
            {"created_at": ""},
            {"created_at": "2022-10-10T06:21:53-07:00", "orders": {"updated_at": "", "deleted": {"deleted_at": ""}}},
        ),
        # state is None
        (
            {"created_at": "2022-10-10T06:21:53-07:00"},
            {"created_at": None},
            {"created_at": "2022-10-10T06:21:53-07:00", "orders": {"updated_at": "", "deleted": {"deleted_at": ""}}},
        ),
        # last rec cursor is None
        ({"created_at": None}, {"created_at": None}, {"created_at": "", "orders": {"updated_at": "", "deleted": {"deleted_at": ""}}}),
        # last rec cursor is empty str
        ({"created_at": ""}, {"created_at": "null"}, {"created_at": "null", "orders": {"updated_at": "", "deleted": {"deleted_at": ""}}}),
        # no values at all
        ({}, {}, {"created_at": "", "orders": {"updated_at": "", "deleted": {"deleted_at": ""}}}),
    ],
    ids=[
        "no init state",
        "state is empty str",
        "state is None",
        "last rec cursor is None",
        "last rec cursor is empty str",
        "no values at all",
    ],
)
def test_get_updated_state(config, last_record, current_state, expected) -> None:
    stream = OrderRefunds(config)
    assert stream.get_updated_state(current_state, last_record) == expected


def test_parse_response_with_bad_json(config, response_with_bad_json) -> None:
    stream = Customers(config)
    assert list(stream.parse_response(response_with_bad_json)) == [{}]


@pytest.mark.parametrize(
    "shop, expected",
    [
        ("test-store", "test-store"),
        ("test-store.myshopify.com", "test-store"),
        ("https://test-store.myshopify.com", "test-store"),
        ("https://test-store.myshopify.com/", "test-store"),
        ("http://test-store.myshopify.com/", "test-store"),
        ("https://Test-Store.myshopify.com", "test-store"),
        ("TEST-STORE", "test-store"),
        ("TEST-STORE.MYSHOPIFY.COM", "test-store"),
        ("  test-store  ", "test-store"),
        ("test-store.myshopify.com/", "test-store"),
    ],
    ids=[
        "bare",
        "full-domain",
        "https",
        "https-slash",
        "http-slash",
        "mixed-case",
        "bare-upper",
        "full-domain-upper",
        "whitespace",
        "bare-slash",
    ],
)
def test_get_shop_name(config, shop, expected) -> None:
    source = SourceShopify()
    config["shop"] = shop
    actual = source.get_shop_name(config)
    assert actual == expected


@pytest.mark.parametrize(
    "shop",
    [
        "https://test-store.myshopify.com/admin",
        "test-store.myshopify.com/admin/api",
        "https://test-store.myshopify.com?foo=bar",
        "https://test-store.myshopify.com#section",
        "test store",
        "test_store",
        "",
        "   ",
        "https://",
        "-test-store",
        "test-store-",
        None,
        12345,
    ],
    ids=[
        "path-scheme",
        "path-bare",
        "query",
        "fragment",
        "space",
        "underscore",
        "empty",
        "whitespace",
        "scheme-only",
        "leading-hyphen",
        "trailing-hyphen",
        "none",
        "non-string",
    ],
)
def test_get_shop_name_invalid(config, shop) -> None:
    source = SourceShopify()
    config["shop"] = shop
    with pytest.raises(ShopifyWrongShopNameError):
        source.get_shop_name(config)


@pytest.mark.parametrize(
    "config, expected_stream_class",
    [
        ({"fetch_transactions_user_id": False}, TransactionsGraphql),
        ({"fetch_transactions_user_id": True}, Transactions),
        ({}, TransactionsGraphql),
    ],
    ids=["don't fetch user_id", "fetch user id", "unset config value shouldn't fetch user_id"],
)
def test_select_transactions_stream(config, expected_stream_class):
    config["shop"] = "test-store"
    config["credentials"] = {"auth_method": "api_password", "api_password": "shppa_123"}
    config["authenticator"] = ShopifyAuthenticator(config)

    source = SourceShopify()
    actual = source.select_transactions_stream(config)
    assert type(actual) == expected_stream_class


@pytest.mark.parametrize(
    "read_records, expected_shop_id, expected_error",
    [
        pytest.param([{"id": "12345"}], "12345", None, id="test_shop_name_exists"),
        pytest.param([], None, AirbyteTracedException, id="test_shop_name_does_not_exist"),
    ],
)
def test_get_shop_id(config, read_records, expected_shop_id, expected_error):
    check_test = ConnectionCheckTest(config)

    with patch.object(Shop, "read_records", return_value=read_records):
        if expected_error:
            with pytest.raises(expected_error):
                check_test.get_shop_id()
        else:
            actual_shop_id = check_test.get_shop_id()
            assert actual_shop_id == expected_shop_id


def test_test_connection(config):
    config.pop("shop", None)
    check_test = ConnectionCheckTest(config)
    expected = (False, "The `Shopify Store` name is missing. Make sure it's entered and valid.")
    assert check_test.test_connection() == expected


def test_format_stream_name() -> None:
    source = SourceShopify()
    assert source.format_stream_name("test_stream") == "TestStream"


def test_user_scopes_generate_full_list_of_streams(config, mocker):
    source = SourceShopify()

    # the list of the scopes we expect user to have
    expected_user_scopes = [
        "read_customers",
        "read_orders",
        "read_draft_orders",
        "read_products",
        "read_inventory",
        "read_publications",
        "read_content",
        "read_price_rules",
        "read_discounts",
        "read_locations",
        "read_inventory",
        "read_merchant_managed_fulfillment_orders",
        "read_shipping",
        "read_shopify_payments_payouts",
        "read_online_store_pages",
    ]

    # patch the output for the critical methods
    mocker.patch.object(ShopifyAuthenticator, "get_auth_header", return_value={"X-Shopify-Access-Token": "test_toke"})
    mocker.patch.object(ConnectionCheckTest, "get_shop_id", return_value=123456)
    mocker.patch.object(ShopifyScopes, "get_user_scopes", return_value=expected_user_scopes)

    # Adjust this number based on the actual permitted streams
    expected_streams_number = 49
    streams = source.streams(config)
    assert len(streams) == expected_streams_number
    # `market_countries` requires the `read_markets` scope
    assert "market_countries" not in [stream.name for stream in streams]

    expected_user_scopes.append("read_markets")
    streams = source.streams(config)
    assert len(streams) == expected_streams_number + 1
    assert "market_countries" in [stream.name for stream in streams]


@pytest.mark.parametrize(
    "response_data, expected_token",
    [
        # Case 1: Empty page (no nodes, no next page)
        (
            {
                "data": {
                    "deliveryProfiles": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [],
                    }
                }
            },
            None,
        ),
        # Case 2: Parent page iteration (parent page has next page, sub-page does not)
        (
            {
                "data": {
                    "deliveryProfiles": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "parent_cursor"},
                        "nodes": [
                            {
                                "profileLocationGroups": [
                                    {
                                        "locationGroupZones": {
                                            "nodes": [],
                                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                                        }
                                    }
                                ]
                            }
                        ],
                    }
                }
            },
            {"cursor": "parent_cursor", "sub_cursor": None},
        ),
        # Case 3: Sub-page iteration (sub-page has next page regardless of parent page)
        (
            {
                "data": {
                    "deliveryProfiles": {
                        "pageInfo": {"hasNextPage": False, "endCursor": "parent_cursor"},
                        "nodes": [
                            {
                                "profileLocationGroups": [
                                    {
                                        "locationGroupZones": {
                                            "nodes": [],
                                            "pageInfo": {"hasNextPage": True, "endCursor": "sub_cursor"},
                                        }
                                    }
                                ]
                            }
                        ],
                    }
                }
            },
            {"cursor": None, "sub_cursor": "sub_cursor"},
        ),
    ],
)
def test_countries_next_page_token(config, response_data, expected_token):
    config["shop"] = "test-store"
    config["credentials"] = {"auth_method": "api_password", "api_password": "shppa_123"}
    config["authenticator"] = ShopifyAuthenticator(config)

    # Instantiate the Countries stream with a dummy config.
    stream = Countries(config=config, parent=None)

    response_body = json.dumps(response_data)
    response = requests.Response()
    response.status_code = 200
    response._content = response_body.encode("utf-8")

    token = stream.next_page_token(response)
    assert token == expected_token


def test_countries_process_country(config, countries_record_data, countries_expected_record_data):
    config["credentials"] = {"auth_method": "api_password", "api_password": "shppa_123"}
    config["authenticator"] = ShopifyAuthenticator(config)

    # Instantiate the Countries stream with a dummy config.
    stream = Countries(config=config, parent=None)
    assert stream._process_country(countries_record_data) == countries_expected_record_data


def test_countries_request_body_json(config):
    config["shop"] = "test-store"
    config["credentials"] = {"auth_method": "api_password", "api_password": "shppa_123"}
    config["authenticator"] = ShopifyAuthenticator(config)

    # Instantiate the Countries stream with a dummy config.
    stream = Countries(config=config, parent=None)
    stream_slice = {"parent": {"profile_location_groups": [{"locationGroup": {"id": "location/group/id"}}]}}
    request_body = stream.request_body_json(stream_slice=stream_slice, stream_state={})

    expected_request_body = {
        "query": """query DeliveryZoneList {
  deliveryProfiles(
    first: 1
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      profileLocationGroups(
        locationGroupId: "location/group/id"
      ) {
        locationGroupZones(
          first: 100
        ) {
          nodes {
            zone {
              id
              name
              countries {
                id
                name
                translated_name: translatedName
                code {
                  country_code: countryCode
                  rest_of_world: restOfWorld
                }
                provinces {
                  id
                  name
                  code
                  translated_name: translatedName
                }
              }
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
  }
}"""
    }
    assert request_body == expected_request_body


def test_countries_parse_response(config, countries_response_data, countries_expected_record_data):
    config["credentials"] = {"auth_method": "api_password", "api_password": "shppa_123"}
    config["authenticator"] = ShopifyAuthenticator(config)

    # Instantiate the Countries stream with a dummy config.
    stream = Countries(config=config, parent=None)
    response = MagicMock(status_code=requests.codes.OK)
    response.json.return_value = countries_response_data

    records = stream.parse_response(response)
    expected_records = [
        countries_expected_record_data,
    ]
    assert list(records) == expected_records


def test_market_countries_request_body_json(config):
    config["shop"] = "test-store"
    stream = MarketCountries(config)
    request_body = stream.request_body_json(stream_state={}, next_page_token={"cursor": "market_cursor", "sub_cursor": "regions_cursor"})

    expected_request_body = {
        "query": """query MarketCountriesList {
  markets(
    first: 1
    after: "market_cursor"
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      name
      handle
      status
      type
      conditions {
        regionsCondition {
          regions(
            first: 250
            after: "regions_cursor"
          ) {
            nodes {
              __typename
              ... on MarketRegionCountry {
                id
                name
                code
                currency {
                  currency_code: currencyCode
                }
              }
              ... on MarketRegionSubdivision {
                id
                name
                code
                country {
                  code
                  name
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
      }
      delivery {
        shipping {
          is_enabled: isEnabled
          option_definitions: optionDefinitions(
            first: 250
          ) {
            nodes {
              __typename
              id
              currency
              description
              is_active: isActive
              free_delivery_minimum_value: freeDeliveryMinimumValue {
                amount
                currency_code: currencyCode
              }
              ... on DeliveryFlatRateOptionDefinition {
                name
              }
              ... on DeliveryWeightBasedOptionDefinition {
                name
              }
              ... on DeliveryValueBasedOptionDefinition {
                name
              }
            }
          }
        }
      }
    }
  }
}"""
    }
    assert request_body == expected_request_body


def _markets_response(
    markets_has_next: bool,
    regions_has_next: bool,
    market_id: str = "gid://shopify/Market/1",
    regions: list = (),
    markets_cursor: str = "market_cursor",
    regions_cursor: str = "regions_cursor",
) -> dict:
    return {
        "data": {
            "markets": {
                "pageInfo": {"hasNextPage": markets_has_next, "endCursor": markets_cursor},
                "nodes": [
                    {
                        "id": market_id,
                        "conditions": {
                            "regionsCondition": {
                                "regions": {
                                    "nodes": list(regions),
                                    "pageInfo": {"hasNextPage": regions_has_next, "endCursor": regions_cursor},
                                }
                            }
                        },
                    }
                ],
            }
        }
    }


@pytest.mark.parametrize(
    "response_data, expected_token",
    [
        pytest.param(_markets_response(markets_has_next=False, regions_has_next=False), None, id="last_page"),
        pytest.param(
            _markets_response(markets_has_next=True, regions_has_next=False),
            {"cursor": "market_cursor", "sub_cursor": None},
            id="next_market",
        ),
        pytest.param(
            _markets_response(markets_has_next=True, regions_has_next=True),
            {"cursor": None, "sub_cursor": "regions_cursor"},
            id="next_regions_page_of_the_same_market_first",
        ),
        pytest.param({"data": {"markets": {"pageInfo": {"hasNextPage": False}, "nodes": []}}}, None, id="no_markets"),
        pytest.param({"data": None}, None, id="no_data"),
    ],
)
def test_market_countries_next_page_token(config, response_data, expected_token):
    stream = MarketCountries(config)
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(response_data).encode("utf-8")
    assert stream.next_page_token(response) == expected_token


_LOCATION_MARKET_PAGE = {
    "data": {
        "markets": {
            "pageInfo": {"hasNextPage": True, "endCursor": "m2"},
            "nodes": [{"id": "gid://shopify/Market/5", "type": "LOCATION", "conditions": None, "delivery": {"shipping": None}}],
        }
    }
}


def test_market_countries_market_without_regions_condition_is_skipped(config):
    """LOCATION / COMPANY_LOCATION markets can come without `conditions`: no records, pagination moves on to the next market."""
    stream = MarketCountries(config)
    response = MagicMock(status_code=requests.codes.OK)
    response.json.return_value = _LOCATION_MARKET_PAGE
    assert list(stream.parse_response(response)) == []
    assert stream.next_page_token(response) == {"cursor": "m2", "sub_cursor": None}


@pytest.mark.parametrize(
    "make_stream",
    [
        pytest.param(lambda config: Countries(config=config, parent=MagicMock()), id="countries"),
        pytest.param(MarketCountries, id="market_countries"),
    ],
)
@pytest.mark.parametrize(
    "errors, expected_failure_type",
    [
        pytest.param(
            [{"message": "Throttled", "extensions": {"code": "THROTTLED"}}], FailureType.transient_error, id="throttled_is_transient"
        ),
        pytest.param(
            [{"message": "Access denied for markets field.", "extensions": {"code": "ACCESS_DENIED"}}],
            FailureType.system_error,
            id="access_denied_is_a_system_error",
        ),
    ],
)
@pytest.mark.parametrize(
    "data_for",
    [
        pytest.param(lambda field: None, id="data_null"),
        pytest.param(lambda field: {field: None}, id="root_field_null"),
        pytest.param(
            lambda field: {field: {"pageInfo": {"hasNextPage": False}, "nodes": [{"id": "gid://shopify/Market/1", "conditions": None}]}},
            id="partial_data_with_nodes",
        ),
    ],
)
def test_graphql_full_refresh_stream_fails_on_graphql_errors(config, make_stream, errors, expected_failure_type, data_for):
    """
    A 200 response with GraphQL `errors` has no usable page (`data` absent, null, or partial per GraphQL spec 7.1.2):
    treating it as empty would mark an incomplete snapshot as complete, so the stream fails before yielding anything.
    """
    stream = make_stream(config)
    response = MagicMock(status_code=requests.codes.OK)
    response.json.return_value = {"data": data_for(stream.response_field), "errors": errors}
    with pytest.raises(AirbyteTracedException) as exc_info:
        next(stream.parse_response(response))
    assert exc_info.value.failure_type == expected_failure_type
    assert errors[0]["message"] in exc_info.value.message


def _graphql_response(body: dict) -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(body).encode("utf-8")
    return response


@pytest.mark.parametrize(
    "make_stream",
    [
        pytest.param(lambda config: Countries(config=config, parent=MagicMock()), id="countries"),
        pytest.param(MarketCountries, id="market_countries"),
    ],
)
def test_graphql_full_refresh_error_handler_retries_throttled_pages_only(config, make_stream):
    """Only a throttled 200 is retried by the HTTP client; other GraphQL errors reach `parse_response`, which fails the stream."""
    handler = make_stream(config).get_error_handler()

    throttled = handler.interpret_response(_graphql_response({"errors": [{"message": "Throttled", "extensions": {"code": "THROTTLED"}}]}))
    assert (throttled.response_action, throttled.failure_type) == (ResponseAction.RETRY, FailureType.transient_error)

    denied = handler.interpret_response(
        _graphql_response({"data": None, "errors": [{"message": "Access denied", "extensions": {"code": "ACCESS_DENIED"}}]})
    )
    assert denied.response_action == ResponseAction.SUCCESS

    assert handler.interpret_response(_graphql_response({"data": {"markets": {"nodes": []}}})).response_action == ResponseAction.SUCCESS


def _market_region_country(region_id: int, code: str) -> dict:
    return {"__typename": "MarketRegionCountry", "id": f"gid://shopify/MarketRegionCountry/{region_id}", "name": code, "code": code}


def _query_cursors(query: str) -> tuple:
    markets_cursor = re.search(r'markets\(\s*first: 1\s*after: "([^"]+)"', query)
    regions_cursor = re.search(r'regions\(\s*first: 250\s*after: "([^"]+)"', query)
    return (markets_cursor and markets_cursor.group(1), regions_cursor and regions_cursor.group(1))


def _market_driven_shop_callback(responses_by_cursors: dict, seen_cursors: list):
    def graphql_callback(request, context):
        query = request.json()["query"]
        if query.startswith("query ShopFeatures"):
            return {"data": {"shop": {"features": {"marketDrivenShipping": True}}}}
        cursors = _query_cursors(query)
        seen_cursors.append(cursors)
        return responses_by_cursors[cursors]

    return graphql_callback


def _read_full_refresh(stream):
    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name=stream.name, json_schema=stream.get_json_schema(), supported_sync_modes=[SyncMode.full_refresh]),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    return stream.read(configured_stream, logging.getLogger("airbyte"), DebugSliceLogger(), {}, None, InternalConfig())


def test_market_countries_read_retries_a_throttled_page(requests_mock, config):
    """A throttled page is re-requested by the HTTP client (same cursors); the retried page's records are emitted once."""
    page_responses = [
        {"errors": [{"message": "Throttled", "extensions": {"code": "THROTTLED"}}]},
        _markets_response(False, False, "gid://shopify/Market/2", [_market_region_country(21, "DE")]),
    ]
    seen_cursors = []

    def graphql_callback(request, context):
        query = request.json()["query"]
        if query.startswith("query ShopFeatures"):
            return {"data": {"shop": {"features": {"marketDrivenShipping": True}}}}
        seen_cursors.append(_query_cursors(query))
        return page_responses.pop(0)

    requests_mock.post("https://test-shop.myshopify.com/admin/api/2026-07/graphql.json", json=graphql_callback)

    stream = MarketCountries(config)
    records = [message for message in _read_full_refresh(stream) if isinstance(message, dict)]

    assert seen_cursors == [(None, None), (None, None)]
    assert [record["id"] for record in records] == ["gid://shopify/MarketRegionCountry/21"]
    assert stream.state == {"__ab_full_refresh_sync_complete": True}


def test_market_countries_read_fails_on_errored_page_and_keeps_the_last_checkpoint(requests_mock, config):
    """
    A page answered with GraphQL `errors` must not complete the resumable full refresh: the stream fails and the
    next attempt resumes from the last checkpoint instead of overwriting the destination with a partial snapshot.
    """
    responses_by_cursors = {
        ("m1", "r1"): _markets_response(True, True, "gid://shopify/Market/2", [_market_region_country(21, "DE")], "m2", "r2"),
        ("m1", "r2"): {"data": None, "errors": [{"message": "Access denied for markets field.", "extensions": {"code": "ACCESS_DENIED"}}]},
    }
    requests_mock.post(
        "https://test-shop.myshopify.com/admin/api/2026-07/graphql.json",
        json=_market_driven_shop_callback(responses_by_cursors, []),
    )

    stream = MarketCountries(config)
    stream.state = {"cursor": "m1", "sub_cursor": "r1"}
    with pytest.raises(AirbyteTracedException):
        list(_read_full_refresh(stream))
    assert stream.state == {"cursor": "m1", "sub_cursor": "r2"}


def test_market_countries_resumes_from_checkpointed_cursors(requests_mock, config):
    """
    A fresh stream instance must honor the cursors handed back by the CDK (resumable full refresh):
    the market cursor is kept while paging the regions of the same market, and the regions cursor
    is dropped when moving on to the next market.
    """
    responses_by_cursors = {
        # resumed mid-way: 2nd page of regions of market 2, the markets `endCursor` (m2) is only used once its regions are exhausted
        ("m1", "r1"): _markets_response(True, True, "gid://shopify/Market/2", [_market_region_country(21, "DE")], "m2", "r2"),
        ("m1", "r2"): _markets_response(True, False, "gid://shopify/Market/2", [_market_region_country(22, "FR")], "m2", "r2"),
        ("m2", None): _markets_response(False, False, "gid://shopify/Market/3", [_market_region_country(31, "CA")]),
    }
    seen_cursors = []
    requests_mock.post(
        "https://test-shop.myshopify.com/admin/api/2026-07/graphql.json",
        json=_market_driven_shop_callback(responses_by_cursors, seen_cursors),
    )

    stream = MarketCountries(config)
    stream.state = {"cursor": "m1", "sub_cursor": "r1"}
    records = [message for message in _read_full_refresh(stream) if isinstance(message, dict)]

    assert seen_cursors == [("m1", "r1"), ("m1", "r2"), ("m2", None)]
    assert stream.state == {"__ab_full_refresh_sync_complete": True}
    assert [record["id"] for record in records] == [
        "gid://shopify/MarketRegionCountry/21",
        "gid://shopify/MarketRegionCountry/22",
        "gid://shopify/MarketRegionCountry/31",
    ]


def test_market_countries_parse_response(config):
    stream = MarketCountries(config)
    response = MagicMock(status_code=requests.codes.OK)
    response.json.return_value = {
        "data": {
            "markets": {
                "pageInfo": {"hasNextPage": False, "endCursor": None},
                "nodes": [
                    {
                        "id": "gid://shopify/Market/100",
                        "name": "Europe",
                        "handle": "eu",
                        "status": "ACTIVE",
                        "type": "REGION",
                        "conditions": {
                            "regionsCondition": {
                                "regions": {
                                    "nodes": [
                                        {
                                            "__typename": "MarketRegionCountry",
                                            "id": "gid://shopify/MarketRegionCountry/1",
                                            "name": "Germany",
                                            "code": "DE",
                                            "currency": {"currency_code": "EUR"},
                                        },
                                        # region type not covered by the query's inline fragments
                                        {"__typename": "MarketRegionFuture"},
                                        {
                                            "__typename": "MarketRegionCountry",
                                            "id": "gid://shopify/MarketRegionCountry/2",
                                            "name": "France",
                                            "code": "FR",
                                            "currency": {"currency_code": "EUR"},
                                        },
                                        {
                                            "__typename": "MarketRegionSubdivision",
                                            "id": "gid://shopify/MarketRegionSubdivision/3",
                                            "name": "Corsica",
                                            "code": "20R",
                                            "country": {"code": "FR", "name": "France"},
                                        },
                                        {
                                            "__typename": "MarketRegionSubdivision",
                                            "id": "gid://shopify/MarketRegionSubdivision/4",
                                            "name": "Bavaria",
                                            "code": "BY",
                                            "country": {"code": "DE", "name": "Germany"},
                                        },
                                    ],
                                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                                }
                            }
                        },
                        "delivery": {
                            "shipping": {
                                "is_enabled": True,
                                "option_definitions": {
                                    "nodes": [
                                        {
                                            "__typename": "DeliveryFlatRateOptionDefinition",
                                            "id": "gid://shopify/DeliveryFlatRateOptionDefinition/10",
                                            "currency": "EUR",
                                            "description": None,
                                            "is_active": True,
                                            "free_delivery_minimum_value": {"amount": "50.0", "currency_code": "EUR"},
                                            "name": "Standard",
                                        },
                                        {
                                            "__typename": "DeliveryCarrierCalculatedOptionDefinition",
                                            "id": "gid://shopify/DeliveryCarrierCalculatedOptionDefinition/11",
                                            "currency": "EUR",
                                            "description": "DHL",
                                            "is_active": False,
                                            "free_delivery_minimum_value": None,
                                        },
                                    ]
                                },
                            }
                        },
                    }
                ],
            }
        }
    }

    expected_shipping_options = [
        {
            "id": 10,
            "type": "DeliveryFlatRateOptionDefinition",
            "name": "Standard",
            "description": None,
            "currency": "EUR",
            "is_active": True,
            "free_delivery_minimum_value": {"amount": 50.0, "currency_code": "EUR"},
        },
        {
            "id": 11,
            "type": "DeliveryCarrierCalculatedOptionDefinition",
            "name": None,
            "description": "DHL",
            "currency": "EUR",
            "is_active": False,
            "free_delivery_minimum_value": None,
        },
    ]
    market_fields = {
        "market_id": 100,
        "market_name": "Europe",
        "market_handle": "eu",
        "market_status": "ACTIVE",
        "market_type": "REGION",
        "shipping_enabled": True,
        "shipping_options": expected_shipping_options,
        "shop_url": "test-shop",
    }
    no_subdivision = {"subdivision_name": None, "subdivision_code": None}
    records = list(stream.parse_response(response))
    assert records == [
        {
            "id": "gid://shopify/MarketRegionCountry/1",
            "name": "Germany",
            "code": "DE",
            "currency_code": "EUR",
            **no_subdivision,
            **market_fields,
        },
        {
            "id": "gid://shopify/MarketRegionCountry/2",
            "name": "France",
            "code": "FR",
            "currency_code": "EUR",
            **no_subdivision,
            **market_fields,
        },
        {
            "id": "gid://shopify/MarketRegionSubdivision/3",
            "name": "France",
            "code": "FR",
            "subdivision_name": "Corsica",
            "subdivision_code": "20R",
            "currency_code": None,
            **market_fields,
        },
        {
            "id": "gid://shopify/MarketRegionSubdivision/4",
            "name": "Germany",
            "code": "DE",
            "subdivision_name": "Bavaria",
            "subdivision_code": "BY",
            "currency_code": None,
            **market_fields,
        },
    ]
    schema = stream.get_json_schema()
    for record in records:
        jsonschema.validate(record, schema)


def test_market_countries_parse_response_subdivision_only_market(config):
    """A market limited to a single US state has no `MarketRegionCountry` node at all."""
    stream = MarketCountries(config)
    response = MagicMock(status_code=requests.codes.OK)
    payload = _markets_response(
        False,
        False,
        "gid://shopify/Market/7",
        [
            {
                "__typename": "MarketRegionSubdivision",
                "id": "gid://shopify/MarketRegionSubdivision/70",
                "name": "California",
                "code": "CA",
                "country": {"code": "US", "name": "United States"},
            }
        ],
    )
    # `shipping` is null when the market inherits its shipping configuration from a parent market
    payload["data"]["markets"]["nodes"][0]["delivery"] = {"shipping": None}
    response.json.return_value = payload
    records = list(stream.parse_response(response))
    assert len(records) == 1
    assert (records[0]["shipping_enabled"], records[0]["shipping_options"]) == (None, None)
    assert records[0]["id"] == "gid://shopify/MarketRegionSubdivision/70"
    assert (records[0]["code"], records[0]["name"]) == ("US", "United States")
    assert (records[0]["subdivision_code"], records[0]["subdivision_name"]) == ("CA", "California")
    assert records[0]["currency_code"] is None
    assert records[0]["market_id"] == 7
    jsonschema.validate(records[0], stream.get_json_schema())
