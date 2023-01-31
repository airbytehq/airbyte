#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import responses
from airbyte_cdk.models import SyncMode
from source_chargebee.streams import Addon, AttachedItem, Coupon, Customer, Event, Invoice, Item, ItemPrice, Order, Plan, Subscription


@responses.activate
def test_addon_stream(test_config_v1, addons_response):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/addons",
        json=addons_response,
    )
    stream = Addon(start_date=test_config_v1["start_date"])
    records = [r for r in stream.read_records(SyncMode.incremental, None, None, None)]
    assert len(records) == 5
    assert len(responses.calls) == 1


@responses.activate
def test_plan_stream(test_config_v1, plans_response):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/plans",
        json=plans_response,
    )
    stream = Plan(start_date=test_config_v1["start_date"])
    records = [r for r in stream.read_records(SyncMode.incremental, None, None, None)]
    assert len(records) == 5
    assert len(responses.calls) == 1


@responses.activate
def test_coupon_stream(test_config_v2, coupons_response):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/coupons",
        json=coupons_response,
    )
    stream = Coupon(start_date=test_config_v2["start_date"])
    records = [r for r in stream.read_records(SyncMode.incremental, None, None, None)]
    assert len(records) == 5
    assert len(responses.calls) == 1


@responses.activate
def test_customer_stream(test_config_v2, customers_response):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/customers",
        json=customers_response,
    )
    stream = Customer(start_date=test_config_v2["start_date"])
    records = [r for r in stream.read_records(SyncMode.incremental, None, None, None)]
    assert len(records) == 5
    assert len(responses.calls) == 1


@responses.activate
def test_order_stream(test_config_v2, orders_response):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/orders",
        json=orders_response,
    )
    stream = Order(start_date=test_config_v2["start_date"])
    records = [r for r in stream.read_records(SyncMode.incremental, None, None, None)]
    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_event_stream(test_config_v2, events_response):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/events",
        json=events_response,
    )
    stream = Event(start_date=test_config_v2["start_date"])
    records = [r for r in stream.read_records(SyncMode.incremental, None, None, None)]
    assert len(records) == 3
    assert len(responses.calls) == 1


@responses.activate
def test_invoice_stream(test_config_v2, invoices_response):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/invoices",
        json=invoices_response,
    )
    stream = Invoice(start_date=test_config_v2["start_date"])
    records = [r for r in stream.read_records(SyncMode.incremental, None, None, None)]
    assert len(records) == 5
    assert len(responses.calls) == 1


@responses.activate
def test_subscription_stream(test_config_v2, subscriptions_response):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/subscriptions",
        json=subscriptions_response,
    )
    stream = Subscription(start_date=test_config_v2["start_date"])
    records = [r for r in stream.read_records(SyncMode.incremental, None, None, None)]
    assert len(records) == 5
    assert len(responses.calls) == 1


@responses.activate
def test_item_stream(test_config_v2, items_response):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/items",
        json=items_response,
    )
    stream = Item(start_date=test_config_v2["start_date"])
    records = [r for r in stream.read_records(SyncMode.incremental, None, None, None)]
    assert len(records) == 5
    assert len(responses.calls) == 1


@responses.activate
def test_item_price_stream(test_config_v2, item_prices_response):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/item_prices",
        json=item_prices_response,
    )
    stream = ItemPrice(start_date=test_config_v2["start_date"])
    records = [r for r in stream.read_records(SyncMode.incremental, None, None, None)]
    assert len(records) == 5
    assert len(responses.calls) == 1


@responses.activate
def test_attached_item_stream(test_config_v2, attached_items_response):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/items/cbdemo_standard/attached_items",
        json=attached_items_response,
    )
    stream = AttachedItem(start_date=test_config_v2["start_date"])
    records = [r for r in stream.read_records(SyncMode.incremental, None, {"item_id": "cbdemo_standard"}, None)]
    assert len(records) == 2
    assert len(responses.calls) == 1


def test_starting_point(test_config_v2):
    stream = Subscription(start_date=test_config_v2["start_date"])

    assert stream.get_starting_point(None, "123") == stream._start_date
    assert stream.get_starting_point({stream.cursor_field: 1621666664}, "some_id") == stream._start_date
    assert stream.get_starting_point({"some_id": {}}, "some_id") == stream._start_date
    assert stream.get_starting_point({"some_id": {stream.cursor_field: 1621666665}}, "some_id") == 1621666665
    assert stream.get_starting_point({"some_id": {stream.cursor_field: 1621666663}}, "some_id") == 1621666664


def test_updated_state(test_config_v2):
    stream = Subscription(start_date=test_config_v2["start_date"])

    assert stream.get_updated_state({}, {}) == {}
    assert stream.get_updated_state({stream.cursor_field: 1621666664}, {}) == {stream.cursor_field: 1621666664}
    assert stream.get_updated_state({}, {stream.cursor_field: 1621666665}) == {stream.cursor_field: 1621666665}
