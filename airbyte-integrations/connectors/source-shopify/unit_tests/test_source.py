import pytest
from source_shopify.auth import ShopifyAuthenticator
from source_shopify.source import (
    AbandonedCheckouts,
    Collects,
    CustomCollections,
    Customers,
    DiscountCodes,
    DraftOrders,
    FulfillmentOrders,
    Fulfillments,
    InventoryLevels,
    Locations,
    Metafields,
    OrderRefunds,
    OrderRisks,
    Orders,
    Pages,
    PriceRules,
    Products,
    Shop,
    TenderTransactions,
    Transactions,
)


@pytest.fixture
def test_config(basic_config):
    basic_config["start_date"] = "2020-11-01"
    basic_config["authenticator"] = ShopifyAuthenticator(basic_config)
    return basic_config


@pytest.mark.parametrize(
    "stream,expected_path",
    [
        (Customers, "customers.json"),
        (Orders, "orders.json"),
        (DraftOrders, "draft_orders.json"),
        (Products, "products.json"),
        (AbandonedCheckouts, "checkouts.json"),
        (Metafields, "metafields.json"),
        (Collects, "collects.json"),
        (TenderTransactions, "tender_transactions.json"),
        (Pages, "pages.json"),
        (PriceRules, "price_rules.json"),
        (Locations, "locations.json"),
        (Shop, "shop.json"),
        (CustomCollections, "custom_collections.json"),
    ],
)
def test_customers_path(stream, expected_path, test_config):
    stream = stream(test_config)
    assert stream.path() == expected_path


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
def test_customers_path_with_stream_slice_param(stream, stream_slice, expected_path, test_config):
    stream = stream(test_config)
    assert stream.path(stream_slice) == expected_path
