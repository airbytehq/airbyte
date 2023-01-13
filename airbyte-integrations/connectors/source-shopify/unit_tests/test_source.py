#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

import pytest
from source_shopify.auth import ShopifyAuthenticator
from source_shopify.source import (
    AbandonedCheckouts,
    Articles,
    Blogs,
    Collects,
    CustomCollections,
    Customers,
    DiscountCodes,
    DraftOrders,
    FulfillmentOrders,
    Fulfillments,
    InventoryLevels,
    Locations,
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
    SourceShopify,
    TenderTransactions,
    Transactions,
)


@pytest.fixture
def config(basic_config):
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
        (MetafieldCustomers, {"id": 123}, "customers/123/metafields.json"),
        (MetafieldOrders, {"id": 123}, "orders/123/metafields.json"),
        (MetafieldDraftOrders, {"id": 123}, "draft_orders/123/metafields.json"),
        (MetafieldProducts, {"id": 123}, "products/123/metafields.json"),
        (MetafieldProductVariants, {"variants": 123}, "variants/123/metafields.json"),
        (MetafieldSmartCollections, {"id": 123}, "smart_collections/123/metafields.json"),
        (MetafieldCollections, {"collection_id": 123}, "collections/123/metafields.json"),
        (MetafieldPages, {"id": 123}, "pages/123/metafields.json"),
        (MetafieldLocations, {"id": 123}, "locations/123/metafields.json"),
        (MetafieldShops, None, "metafields.json"),
        (ProductImages, {"product_id": 123}, "products/123/images.json"),
        (ProductVariants, {"product_id": 123}, "products/123/variants.json"),
        (Customers, None, "customers.json"),
        (Orders, None, "orders.json"),
        (DraftOrders, None, "draft_orders.json"),
        (Products, None, "products.json"),
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
def test_customers_path(stream, stream_slice, expected_path, config):
    stream = stream(config)
    if stream_slice:
        result = stream.path(stream_slice)
    else:
        result = stream.path()
    assert result == expected_path


@pytest.mark.parametrize(
    "stream,stream_slice,expected_path",
    [
        (OrderRefunds, {"order_id": 12345}, "orders/12345/refunds.json"),
        (OrderRisks, {"order_id": 12345}, "orders/12345/risks.json"),
        (Transactions, {"order_id": 12345}, "orders/12345/transactions.json"),
        (DiscountCodes, {"price_rule_id": 12345}, "price_rules/12345/discount_codes.json"),
        (InventoryLevels, {"location_id": 12345}, "locations/12345/inventory_levels.json"),
        (FulfillmentOrders, {"order_id": 12345}, "orders/12345/fulfillment_orders.json"),
        (Fulfillments, {"order_id": 12345}, "orders/12345/fulfillments.json"),
    ],
)
def test_customers_path_with_stream_slice_param(stream, stream_slice, expected_path, config):
    stream = stream(config)
    assert stream.path(stream_slice) == expected_path


def test_check_connection(config, mocker):
    mocker.patch("source_shopify.source.Shop.read_records", return_value=[{"id": 1}])
    source = SourceShopify()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_read_records(config, mocker):
    records = [{"created_at": "2022-10-10T06:21:53-07:00", "orders": {"updated_at": "2022-10-10T06:21:53-07:00"}}]
    stream_slice = records[0]
    stream = OrderRefunds(config)
    mocker.patch("source_shopify.source.IncrementalShopifyStream.read_records", return_value=records)
    assert next(stream.read_records(stream_slice=stream_slice)) == records[0]


@pytest.mark.parametrize(
    "stream, expected",
    [
        (OrderRefunds, {"limit": 250}),
        (Orders, {"limit": 250, "status": "any", "order": "updated_at asc", "updated_at_min": "2020-11-01"}),
        (
            AbandonedCheckouts,
            {"limit": 250, "status": "any", "order": "updated_at asc", "updated_at_min": "2020-11-01"},
        ),
    ],
)
def test_request_params(config, stream, expected):
    assert stream(config).request_params() == expected


def test_get_updated_state(config):
    current_stream_state = {"created_at": ""}
    latest_record = {"created_at": "2022-10-10T06:21:53-07:00"}
    updated_state = {"created_at": "2022-10-10T06:21:53-07:00", "orders": None}
    stream = OrderRefunds(config)
    assert (
        stream.get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)
        == updated_state
    )
