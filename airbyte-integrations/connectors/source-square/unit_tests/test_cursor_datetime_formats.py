# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Regression tests for Square's RFC 3339 cursor timestamp variants."""

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "credentials": {
        "auth_type": "API Key",
        "api_key": "test_api_key",
    },
    "is_sandbox": False,
    "start_date": "2026-07-01",
    "include_deleted_objects": False,
}

_CATALOG_SEARCH_URL = "https://connect.squareup.com/v2/catalog/search"
_PAYMENTS_URL = "https://connect.squareup.com/v2/payments"


def _read(stream_name: str):
    state = (
        StateBuilder()
        .with_stream_state(stream_name, {"updated_at" if stream_name == "items" else "created_at": "2026-07-01T00:00:00Z"})
        .build()
    )
    source = get_source(config=_CONFIG, state=state)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(source, _CONFIG, catalog, state)


def test_items_accepts_whole_second_and_fractional_updated_at_timestamps():
    response = {
        "objects": [
            {
                "id": "item-whole-second",
                "type": "ITEM",
                "updated_at": "2026-07-15T20:21:55Z",
            },
            {
                "id": "item-microsecond",
                "type": "ITEM",
                "updated_at": "2026-07-15T20:21:56.123456Z",
            },
        ]
    }

    with requests_mock.Mocker() as mocker:
        mocker.post(_CATALOG_SEARCH_URL, json=response)
        output = _read("items")

    assert [record.record.data["id"] for record in output.records] == [
        "item-whole-second",
        "item-microsecond",
    ]
    assert output.most_recent_state is not None


def test_payments_accepts_whole_second_and_fractional_created_at_timestamps():
    response = {
        "payments": [
            {
                "id": "payment-whole-second",
                "created_at": "2026-07-15T20:21:55Z",
            },
            {
                "id": "payment-microsecond",
                "created_at": "2026-07-15T20:21:56.123456Z",
            },
        ]
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(_PAYMENTS_URL, json=response)
        output = _read("payments")

    assert [record.record.data["id"] for record in output.records] == [
        "payment-whole-second",
        "payment-microsecond",
    ]
    assert output.most_recent_state is not None
