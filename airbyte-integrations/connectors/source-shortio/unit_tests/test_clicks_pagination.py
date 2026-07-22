# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the `clicks` stream migration to the Short.io statistics API.

Short.io decommissioned the `api-v2.short.cm` host, so the `clicks` stream now
reads raw clicks from `POST https://statistics.short.io/statistics/domain/{domainId}/last_clicks`.

Unlike the old `link_clicks` endpoint (which the connector paginated with a
non-existent `nextPageToken`), `last_clicks` returns a plain array of clicks
ordered newest-first and paginates via a `beforeDate` cursor in the request
body: to fetch the next (older) page you pass the `dt` of the last click you
have seen. When a page comes back empty there are no more clicks.

These tests register a mock that varies its response based on the `beforeDate`
value in the JSON body and assert that the connector:

1. Issues the first request as a POST to `.../last_clicks` with `limit` and no `beforeDate`.
2. Uses the `dt` of the last record as the `beforeDate` cursor for the next page.
3. Stops paginating once an empty page is returned.
4. Emits records from every page.
"""

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "domain_id": "123456",
    "secret_key": "test-secret-key",
    "start_date": "2023-07-30T03:43:59.244Z",
}

_LAST_CLICKS_URL = "https://statistics.short.io/statistics/domain/123456/last_clicks"
_LAST_CLICKS_PATH = "/statistics/domain/123456/last_clicks"

# Three pages worth of clicks, newest first. The `dt` of the last record on each
# page becomes the `beforeDate` cursor the connector must send for the next page.
_PAGE_1 = [
    {"dt": "2024-01-03T00:00:00.000Z", "path": "/a", "method": "GET", "human": True},
    {"dt": "2024-01-02T00:00:00.000Z", "path": "/b", "method": "GET", "human": True},
]
_PAGE_2 = [
    {"dt": "2024-01-01T00:00:00.000Z", "path": "/c", "method": "GET", "human": True},
]


def _callback(request, context):
    """Return pages keyed off the `beforeDate` value in the request body."""
    body = request.json()
    before_date = body.get("beforeDate")
    if before_date is None:
        return _PAGE_1
    if before_date == _PAGE_1[-1]["dt"]:
        return _PAGE_2
    # Cursor advanced past the last page -> no more clicks.
    return []


def _sync():
    catalog = CatalogBuilder().with_stream("clicks", SyncMode.full_refresh).build()
    source = get_source(config=_CONFIG)
    return read(source, _CONFIG, catalog)


def test_clicks_uses_statistics_last_clicks_endpoint():
    """The `clicks` stream POSTs to the new statistics host/path (not the dead `api-v2.short.cm`)."""
    with requests_mock.Mocker() as mocker:
        mocker.post(_LAST_CLICKS_URL, json=_callback)
        _sync()
        requests_made = [r for r in mocker.request_history if r.path == _LAST_CLICKS_PATH]

    assert requests_made, "expected the clicks stream to call the statistics last_clicks endpoint"
    first = requests_made[0]
    assert first.method == "POST", f"last_clicks must be requested with POST, got {first.method}"
    assert first.hostname == "statistics.short.io", f"clicks must hit statistics.short.io, got {first.hostname}"
    assert first.json().get("limit") == 30, f"first request must send a limit, got body={first.json()}"
    assert "beforeDate" not in first.json(), f"first request must not send a beforeDate cursor, got body={first.json()}"


def test_clicks_paginates_with_before_date_cursor():
    """Each subsequent page is fetched with `beforeDate` set to the previous page's last `dt`."""
    with requests_mock.Mocker() as mocker:
        mocker.post(_LAST_CLICKS_URL, json=_callback)
        output = _sync()
        requests_made = [r for r in mocker.request_history if r.path == _LAST_CLICKS_PATH]

    before_dates = [r.json().get("beforeDate") for r in requests_made]
    assert before_dates == [
        None,
        _PAGE_1[-1]["dt"],
        _PAGE_2[-1]["dt"],
    ], f"expected beforeDate cursor to walk backwards through the pages, got {before_dates}"

    emitted = [record.record.data["path"] for record in output.records]
    assert emitted == ["/a", "/b", "/c"], f"expected records from every page, got {emitted}"


def test_clicks_terminates_on_empty_page():
    """A single empty page must stop pagination after one request without looping."""
    with requests_mock.Mocker() as mocker:
        mocker.post(_LAST_CLICKS_URL, json=[])
        output = _sync()
        requests_made = [r for r in mocker.request_history if r.path == _LAST_CLICKS_PATH]

    assert len(requests_made) == 1, f"expected exactly one request when the first page is empty, got {len(requests_made)}"
    assert [record.record.data for record in output.records] == [], "expected no records from an empty first page"
