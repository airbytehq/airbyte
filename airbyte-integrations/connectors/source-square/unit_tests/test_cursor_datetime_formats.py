# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Regression tests for Square's RFC 3339 cursor timestamp variants."""

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
    "credentials": {
        "auth_type": "API Key",
        "api_key": "test_api_key",
    },
    "is_sandbox": False,
    "start_date": _WINDOW_START.strftime("%Y-%m-%d"),
    "include_deleted_objects": False,
}

_CATALOG_SEARCH_URL = "https://connect.squareup.com/v2/catalog/search"
_PAYMENTS_URL = "https://connect.squareup.com/v2/payments"
_CURSOR_FIELDS = {
    "items": "updated_at",
    "categories": "updated_at",
    "discounts": "updated_at",
    "taxes": "updated_at",
    "modifier_list": "updated_at",
    "orders": "updated_at",
    "payments": "created_at",
    "refunds": "created_at",
}


def _read(stream_name: str, cursor_value: str):
    state = StateBuilder().with_stream_state(stream_name, {_CURSOR_FIELDS[stream_name]: cursor_value}).build()
    source = get_source(config=_CONFIG, state=state)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(source, _CONFIG, catalog, state)


def _catalog_response():
    return {
        "objects": [
            {
                "id": "item-microsecond",
                "type": "ITEM",
                "updated_at": _FRACTIONAL_CURSOR,
            },
            {
                "id": "item-whole-second",
                "type": "ITEM",
                "updated_at": _WHOLE_SECOND_CURSOR,
            },
        ]
    }


def _payments_response():
    return {
        "payments": [
            {
                "id": "payment-microsecond",
                "created_at": _FRACTIONAL_CURSOR,
            },
            {
                "id": "payment-whole-second",
                "created_at": _WHOLE_SECOND_CURSOR,
            },
        ]
    }


def test_items_whole_second_record_advances_cursor():
    with requests_mock.Mocker() as mocker:
        mocker.post(_CATALOG_SEARCH_URL, json=_catalog_response())
        output = _read("items", _STATE_VALUE_FRACTIONAL)

    assert [record.record.data["id"] for record in output.records] == [
        "item-microsecond",
        "item-whole-second",
    ]
    assert not output.errors
    assert output.most_recent_state.stream_state.updated_at == _WHOLE_SECOND_CURSOR.replace("Z", ".000000Z")


def test_items_accepts_whole_second_incoming_state():
    with requests_mock.Mocker() as mocker:
        mocker.post(_CATALOG_SEARCH_URL, json=_catalog_response())
        output = _read("items", _STATE_VALUE)

    assert [record.record.data["id"] for record in output.records] == [
        "item-microsecond",
        "item-whole-second",
    ]
    assert not output.errors


def test_payments_whole_second_record_advances_cursor():
    with requests_mock.Mocker() as mocker:
        mocker.get(_PAYMENTS_URL, json=_payments_response())
        output = _read("payments", _STATE_VALUE_FRACTIONAL)

    assert [record.record.data["id"] for record in output.records] == [
        "payment-microsecond",
        "payment-whole-second",
    ]
    assert not output.errors
    assert output.most_recent_state.stream_state.created_at == _WHOLE_SECOND_CURSOR.replace("Z", ".000000Z")


def test_payments_accepts_whole_second_incoming_state():
    with requests_mock.Mocker() as mocker:
        mocker.get(_PAYMENTS_URL, json=_payments_response())
        output = _read("payments", _STATE_VALUE)

    assert [record.record.data["id"] for record in output.records] == [
        "payment-microsecond",
        "payment-whole-second",
    ]
    assert not output.errors
