# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock as requests_mock_lib
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {"api_token": "test_token"}
_URL_BASE = "https://api.simplecast.com"

_CATEGORIES = [
    {"value": "arts", "rss_label": "Arts", "label": "Arts", "subcategories": {"collection": []}},
    {"value": "business", "rss_label": "Business", "label": "Business", "subcategories": {"collection": []}},
    {"value": "comedy", "rss_label": "Comedy", "label": "Comedy", "subcategories": {"collection": []}},
]
_DISTRIBUTION_CHANNELS = [
    {"id": "960dcb10", "name": "Apple Podcasts", "href": f"{_URL_BASE}/distribution_channels/960dcb10"},
    {"id": "00512816", "name": "Google Podcasts", "href": f"{_URL_BASE}/distribution_channels/00512816"},
    {"id": "bb916df4", "name": "Spotify", "href": f"{_URL_BASE}/distribution_channels/bb916df4"},
]

# A read that keeps asking for more pages is cut off here so that a regression fails the assertions instead of hanging.
_MAX_REQUESTS_SERVED = 4


@pytest.mark.parametrize(
    "stream_name, key_field, collection",
    [
        pytest.param("categories", "value", _CATEGORIES, id="categories"),
        pytest.param("distribution_channels", "id", _DISTRIBUTION_CHANNELS, id="distribution_channels"),
    ],
)
def test_lookup_stream_is_read_once_when_api_ignores_paging_params(stream_name, key_field, collection):
    """
    The Simplecast lookup endpoints return their whole list in one response and ignore `offset`/`limit`,
    so the same list comes back whatever the query string says. Each value must be emitted exactly once.
    """
    url = f"{_URL_BASE}/{stream_name}"
    full_list = {"href": url, "collection": collection}

    with requests_mock_lib.Mocker() as mocker:

        def _same_list_whatever_the_query(request, context):
            if mocker.call_count > _MAX_REQUESTS_SERVED:
                return {"href": url, "collection": []}
            return full_list

        mocker.get(url, json=_same_list_whatever_the_query)

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        requests_sent = [(request.path, request.query) for request in mocker.request_history]

    assert [record.record.data[key_field] for record in output.records] == [item[key_field] for item in collection]
    assert requests_sent == [(f"/{stream_name}", "")]
    assert output.errors == []
