# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the Simplecast lookup streams (`categories`, `distribution_channels`).

These endpoints return their whole list in a single response and ignore the `offset` query
parameter, so the connector must request each of them exactly once.
"""

from typing import Any, Dict, List

import pytest
import requests_mock
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {"api_token": "test-token"}
_URL_BASE = "https://api.simplecast.com"

# Safety net: if the connector ever paginates these endpoints again, the fake API starts answering
# with an empty list after this many requests so the test fails on its assertions instead of hanging.
_MAX_FULL_RESPONSES = 5

_CATEGORIES = [
    {"value": "arts", "label": "Arts", "rss_label": "Arts", "subcategories": {"collection": []}},
    {"value": "business", "label": "Business", "rss_label": "Business", "subcategories": {"collection": []}},
    {"value": "comedy", "label": "Comedy", "rss_label": "Comedy", "subcategories": {"collection": []}},
]

_DISTRIBUTION_CHANNELS = [
    {"id": "channel-1", "name": "Apple Podcasts", "href": f"{_URL_BASE}/distribution_channels/channel-1"},
    {"id": "channel-2", "name": "Spotify", "href": f"{_URL_BASE}/distribution_channels/channel-2"},
    {"id": "channel-3", "name": "Overcast", "href": f"{_URL_BASE}/distribution_channels/channel-3"},
]


@pytest.mark.parametrize(
    "stream_name, path, api_records",
    [
        pytest.param("categories", "/categories", _CATEGORIES, id="categories"),
        pytest.param("distribution_channels", "/distribution_channels", _DISTRIBUTION_CHANNELS, id="distribution_channels"),
    ],
)
def test_lookup_stream_is_requested_once_and_emits_each_record_once(stream_name: str, path: str, api_records: List[Dict[str, Any]]):
    """The API returns the full list whatever `offset` is sent, so one request must be the whole read."""

    def full_list_whatever_the_query(request, context) -> Dict[str, Any]:
        if len(mocker.request_history) > _MAX_FULL_RESPONSES:
            return {"collection": []}
        return {"href": f"{_URL_BASE}{path}", "collection": api_records}

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_URL_BASE}{path}", json=full_list_whatever_the_query)
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog, state=StateBuilder().build())

    assert [request.url for request in mocker.request_history] == [f"{_URL_BASE}{path}"]
    assert mocker.request_history[0].headers["Authorization"] == "Bearer test-token"
    assert [record.record.data for record in output.records] == api_records
    assert output.errors == []
