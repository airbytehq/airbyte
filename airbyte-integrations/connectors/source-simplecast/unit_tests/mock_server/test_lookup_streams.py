# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the Simplecast lookup streams `categories` and `distribution_channels`.

`GET /categories` and `GET /distribution_channels` return the whole list in one
response with no paging information and ignore `offset`, so each stream must
request its endpoint exactly once, without an `offset` parameter.
"""

import json
from typing import Any, Dict, List

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ConfigBuilder


_BASE_URL = "https://api.simplecast.com"
_API_TOKEN = "test-api-token"

_CATEGORIES = [
    {"value": "Arts", "label": "Arts", "rss_label": "Arts", "subcategories": {"collection": []}},
    {"value": "Business", "label": "Business", "rss_label": "Business", "subcategories": {"collection": []}},
    {"value": "Comedy", "label": "Comedy", "rss_label": "Comedy", "subcategories": {"collection": []}},
]
_DISTRIBUTION_CHANNELS = [
    {"id": "channel-1", "name": "Apple Podcasts", "href": f"{_BASE_URL}/distribution_channels/channel-1"},
    {"id": "channel-2", "name": "Spotify", "href": f"{_BASE_URL}/distribution_channels/channel-2"},
    {"id": "channel-3", "name": "Overcast", "href": f"{_BASE_URL}/distribution_channels/channel-3"},
]


@pytest.mark.parametrize(
    "stream_name, path, records",
    [
        pytest.param("categories", "/categories", _CATEGORIES, id="categories"),
        pytest.param("distribution_channels", "/distribution_channels", _DISTRIBUTION_CHANNELS, id="distribution_channels"),
    ],
)
def test_lookup_stream_requests_the_full_list_once_without_offset(stream_name: str, path: str, records: List[Dict[str, Any]]):
    """The unpaginated list is requested once, with no `offset`, and each value is emitted once."""
    config = ConfigBuilder().with_api_token(_API_TOKEN).build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    # No query params: HttpMocker matches the query exactly, so any `offset` request is unmatched.
    request = HttpRequest(url=f"{_BASE_URL}{path}", headers={"Authorization": f"Bearer {_API_TOKEN}"})

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"href": f"{_BASE_URL}{path}", "collection": records}), status_code=200))

        output = read(get_source(config=config), config=config, catalog=catalog)

        assert output.errors == []
        assert [message.record.data for message in output.records] == records
        http_mocker.assert_number_of_calls(request, 1)
