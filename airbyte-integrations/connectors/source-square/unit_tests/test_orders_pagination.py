# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the `orders` stream's `cursor`-based pagination on `source-square`.

Square's `POST /v2/orders/search` endpoint defaults to returning at most 500 records per
page and exposes a top-level `cursor` field whenever more results are available. The
stream's manifest must declare a `DefaultPaginator` with a `CursorPagination` strategy
that reads `response.cursor`, injects it back into the request body as `cursor`, and
stops when the response no longer contains a `cursor`. These tests mock the Square API
and assert that the connector follows the cursor across multiple pages, rather than
silently capping at the first page (the bug from oncall #12152).
"""

import json

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "credentials": {
        "auth_type": "API Key",
        "api_key": "test_api_key",
    },
    "is_sandbox": False,
    "start_date": "2021-01-01",
    "include_deleted_objects": False,
}

_LOCATIONS_URL = "https://connect.squareup.com/v2/locations"
_ORDERS_SEARCH_URL = "https://connect.squareup.com/v2/orders/search"


def _order(order_id: str, location_id: str) -> dict:
    return {
        "id": order_id,
        "location_id": location_id,
        "state": "OPEN",
        "created_at": "2024-01-02T10:00:00.000000Z",
        "updated_at": "2024-01-02T10:00:00.000000Z",
        "version": 1,
    }


def _locations_response() -> dict:
    return {
        "locations": [
            {"id": "LOC1", "name": "Loc 1"},
        ]
    }


def _sync(stream_name: str):
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, _CONFIG, catalog)


def test_orders_stream_follows_cursor_across_pages():
    """`orders` stream paginates with Square's `cursor` until the response omits it."""
    page_1 = {
        "orders": [_order(f"order-{i}", "LOC1") for i in range(3)],
        "cursor": "cursor-page-2",
    }
    page_2 = {
        "orders": [_order(f"order-{i}", "LOC1") for i in range(3, 6)],
        "cursor": "cursor-page-3",
    }
    page_3 = {
        "orders": [_order(f"order-{i}", "LOC1") for i in range(6, 8)],
        # No `cursor` in the final page — the paginator must stop here.
    }

    captured_request_bodies: list[dict] = []

    def _orders_response(request, context):
        body = request.json() if request.text else {}
        captured_request_bodies.append(body)
        cursor = body.get("cursor")
        if cursor is None:
            return page_1
        if cursor == "cursor-page-2":
            return page_2
        if cursor == "cursor-page-3":
            return page_3
        raise AssertionError(f"unexpected cursor in request body: {cursor!r}")

    with requests_mock.Mocker() as mocker:
        mocker.get(_LOCATIONS_URL, json=_locations_response())
        mocker.post(_ORDERS_SEARCH_URL, json=_orders_response)
        output = _sync("orders")

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [f"order-{i}" for i in range(8)], f"expected all 8 orders across 3 pages to be emitted, got {emitted_ids}"

    # The first request must NOT carry a cursor; subsequent requests must echo the
    # cursor returned by the previous page in the request body (not the query string).
    assert captured_request_bodies[0].get("cursor") is None, "first orders request should not carry a cursor"
    assert captured_request_bodies[1].get("cursor") == "cursor-page-2"
    assert captured_request_bodies[2].get("cursor") == "cursor-page-3"

    # The paginator must inject `limit` into the request body (not the query string).
    # Square's max limit is 1000; the manifest paginator declares `page_size: 1000`.
    for body in captured_request_bodies:
        assert body.get("limit") == 1000, f"orders request body must declare limit=1000, got {body.get('limit')!r}"


def test_orders_stream_stops_when_cursor_missing():
    """`orders` stream issues exactly one request when the first page has no `cursor`."""
    only_page = {
        "orders": [_order(f"order-{i}", "LOC1") for i in range(2)],
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(_LOCATIONS_URL, json=_locations_response())
        orders_matcher = mocker.post(_ORDERS_SEARCH_URL, json=only_page)
        output = _sync("orders")

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == ["order-0", "order-1"]
    assert (
        orders_matcher.call_count == 1
    ), f"expected exactly one orders request when no cursor is returned, got {orders_matcher.call_count}"


def test_orders_stream_request_body_is_well_formed():
    """`orders` stream sends the expected base body (sort, filter, location_ids) on the first page."""
    page = {"orders": []}

    with requests_mock.Mocker() as mocker:
        mocker.get(_LOCATIONS_URL, json=_locations_response())
        mocker.post(_ORDERS_SEARCH_URL, json=page)
        _sync("orders")
        first_request = mocker.request_history[-1]

    body = json.loads(first_request.text)
    assert body["location_ids"] == ["LOC1"]
    assert body["sort"] == {"sort_field": "UPDATED_AT", "sort_order": "ASC"}
    assert "filter" in body and "date_time_filter" in body["filter"]
    # The hardcoded `limit: "{{ 500 }}"` in `request_body_json` was replaced by the
    # paginator's `page_size_option` (limit=1000). Make sure no stale 500 leaks through.
    assert body["limit"] == 1000
