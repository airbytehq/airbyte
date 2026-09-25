#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
from source_shopify.auth import ShopifyAuthenticator
from source_shopify.streams.streams import Fulfillments, OrderCustomers, OrderRefunds
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache


CUSTOMER_1 = {"id": 100, "email": "a@example.com", "first_name": "A", "updated_at": "2020-01-01T00:00:00-07:00"}
CUSTOMER_2 = {"id": 200, "email": "b@example.com", "first_name": "B", "updated_at": "2019-06-01T00:00:00-07:00"}

ORDERS = [
    {
        "id": 1,
        "updated_at": "2023-01-01T00:00:00-07:00",
        "customer": CUSTOMER_1,
        "refunds": [{"id": 11, "created_at": "2023-01-01T00:00:00-07:00"}],
    },
    # guest checkout: no customer attached to the order
    {"id": 2, "updated_at": "2023-01-02T00:00:00-07:00", "customer": None, "refunds": []},
    {
        "id": 3,
        "updated_at": "2023-01-03T00:00:00-07:00",
        "customer": CUSTOMER_2,
        "refunds": [{"id": 31, "created_at": "2023-01-03T00:00:00-07:00"}],
    },
    # same customer placed a second order
    {"id": 4, "updated_at": "2023-01-04T00:00:00-07:00", "customer": dict(CUSTOMER_1), "refunds": []},
]


@pytest.fixture
def config(basic_config) -> dict:
    basic_config["start_date"] = "2020-11-01"
    basic_config["authenticator"] = ShopifyAuthenticator(basic_config)
    return basic_config


@pytest.fixture(autouse=True)
def reset_stream_state_cache():
    stream_state_cache.cached_state.clear()
    yield
    stream_state_cache.cached_state.clear()


def _read_nested_stream(stream, mocker, parent_records, stream_state=None):
    mocker.patch.object(type(stream.parent_stream), "read_records", return_value=[dict(record) for record in parent_records])
    records = []
    for stream_slice in stream.stream_slices(stream_state=stream_state, sync_mode="incremental"):
        records += list(stream.read_records(stream_slice=stream_slice, sync_mode="incremental"))
    return records


def test_order_customers_flattens_single_nested_object(config, mocker):
    stream = OrderCustomers(config)
    records = _read_nested_stream(stream, mocker, ORDERS)

    assert [record["order_id"] for record in records] == [1, 3, 4]
    assert [record["id"] for record in records] == [100, 200, 100]
    assert [record["order_updated_at"] for record in records] == [order["updated_at"] for order in ORDERS if order["customer"]]
    # customer attributes are flattened to top-level columns
    assert records[0]["email"] == "a@example.com"
    assert records[0]["first_name"] == "A"
    assert records[0]["shop_url"] == config["shop"]


def test_order_customers_skips_guest_checkouts(config, mocker):
    stream = OrderCustomers(config)
    records = _read_nested_stream(stream, mocker, [ORDERS[1]])
    assert records == []


def test_order_customers_stream_definition(config):
    stream = OrderCustomers(config)
    assert stream.primary_key == "order_id"
    assert stream.cursor_field == "order_updated_at"
    schema_properties = stream.get_json_schema()["properties"]
    for field in ("order_id", "order_updated_at", "id", "email", "first_name", "last_name", "phone", "default_address", "shop_url"):
        assert field in schema_properties


def test_order_customers_incremental_filtering(config, mocker):
    stream = OrderCustomers(config)
    state = {"order_updated_at": "2023-01-03T00:00:00-07:00", "orders": {"updated_at": "2023-01-03T00:00:00-07:00"}}
    records = _read_nested_stream(stream, mocker, ORDERS, stream_state=state)

    assert [record["order_id"] for record in records] == [3, 4]
    updated_state = stream.get_updated_state(state, records[-1])
    assert updated_state["order_updated_at"] == "2023-01-04T00:00:00-07:00"
    assert updated_state["orders"]["updated_at"] == "2023-01-04T00:00:00-07:00"


@pytest.mark.parametrize(
    "stream_class, expected_ids",
    [
        (OrderRefunds, [11, 31]),
        (Fulfillments, [12, 32]),
    ],
)
def test_list_nested_streams_are_not_affected(config, mocker, stream_class, expected_ids):
    orders = [
        {**order, "fulfillments": [{"id": order["id"] * 10 + 2, "updated_at": order["updated_at"]}] if order["refunds"] else []}
        for order in ORDERS
    ]
    stream = stream_class(config)
    records = _read_nested_stream(stream, mocker, orders)
    assert [record["id"] for record in records] == expected_ids
