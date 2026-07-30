# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Incremental regression tests for the `orders` per-partition cursor."""

from datetime import datetime, timedelta, timezone

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_NOW = datetime.now(timezone.utc)
_WINDOW_START = _NOW - timedelta(days=1)
_STATE_VALUE = _WINDOW_START.strftime("%Y-%m-%dT%H:%M:%SZ")
_STATE_VALUE_FRACTIONAL = _WINDOW_START.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
_WHOLE_SECOND_CURSOR = (_NOW - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
_FRACTIONAL_CURSOR = (_NOW - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

_CONFIG = {
    "credentials": {"auth_type": "API Key", "api_key": "test_api_key"},
    "is_sandbox": False,
    "start_date": _WINDOW_START.strftime("%Y-%m-%d"),
    "include_deleted_objects": False,
}
_LOCATIONS_URL = "https://connect.squareup.com/v2/locations"
_ORDERS_SEARCH_URL = "https://connect.squareup.com/v2/orders/search"
_PARTITION = {"location_ids": "LOC1", "parent_slice": {}}


def _read(cursor_value: str):
    state = (
        StateBuilder()
        .with_stream_state(
            "orders",
            {
                "use_global_cursor": False,
                "states": [{"partition": _PARTITION, "cursor": {"updated_at": cursor_value}}],
                "state": {"updated_at": cursor_value},
                "lookback_window": 1,
            },
        )
        .build()
    )
    source = get_source(config=_CONFIG, state=state)
    catalog = CatalogBuilder().with_stream("orders", SyncMode.incremental).build()
    orders = {
        "orders": [
            {
                "id": "order-microsecond",
                "location_id": "LOC1",
                "updated_at": _FRACTIONAL_CURSOR,
            },
            {
                "id": "order-whole-second",
                "location_id": "LOC1",
                "updated_at": _WHOLE_SECOND_CURSOR,
            },
        ]
    }
    with requests_mock.Mocker() as mocker:
        mocker.get(_LOCATIONS_URL, json={"locations": [{"id": "LOC1", "name": "Loc 1"}]})
        mocker.post(_ORDERS_SEARCH_URL, json=orders)
        return read(source, _CONFIG, catalog, state)


def test_orders_whole_second_record_advances_per_partition_cursor():
    output = _read(_STATE_VALUE_FRACTIONAL)

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [
        "order-microsecond",
        "order-whole-second",
    ]
    assert output.most_recent_state.stream_state.states == [
        {
            "partition": _PARTITION,
            "cursor": {"updated_at": _WHOLE_SECOND_CURSOR.replace("Z", ".000000Z")},
        }
    ]


def test_orders_accepts_whole_second_incoming_per_partition_state():
    output = _read(_STATE_VALUE)

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [
        "order-microsecond",
        "order-whole-second",
    ]
