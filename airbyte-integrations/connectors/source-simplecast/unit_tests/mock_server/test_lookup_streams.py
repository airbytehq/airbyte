# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_CONFIG = {"api_token": "test-token"}
_URL_BASE = "https://api.simplecast.com"

_CATEGORIES = [
    {"value": "arts", "label": "Arts", "rss_label": "Arts", "subcategories": {"collection": []}},
    {"value": "business", "label": "Business", "rss_label": "Business", "subcategories": {"collection": []}},
    {"value": "comedy", "label": "Comedy", "rss_label": "Comedy", "subcategories": {"collection": []}},
]
_DISTRIBUTION_CHANNELS = [
    {"id": "960dcb10", "name": "Apple Podcasts", "href": f"{_URL_BASE}/distribution_channels/960dcb10"},
    {"id": "00512816", "name": "Google Podcasts", "href": f"{_URL_BASE}/distribution_channels/00512816"},
    {"id": "bb916df4", "name": "Spotify", "href": f"{_URL_BASE}/distribution_channels/bb916df4"},
]


@pytest.mark.parametrize(
    "stream_name, path, key, collection",
    [
        pytest.param("categories", "/categories", "value", _CATEGORIES, id="categories"),
        pytest.param("distribution_channels", "/distribution_channels", "id", _DISTRIBUTION_CHANNELS, id="distribution_channels"),
    ],
)
def test_lookup_stream_is_read_in_one_request_and_emits_each_value_once(stream_name, path, key, collection):
    """
    The lookup endpoints return their whole list in a single response, carry no paging
    information, and ignore `offset`. The stream must request the endpoint exactly once,
    with no paging parameters, and emit each value exactly once.
    """
    request = HttpRequest(url=f"{_URL_BASE}{path}", query_params={}, headers={"Authorization": "Bearer test-token"})
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"href": f"{_URL_BASE}{path}", "collection": collection}), status_code=200))

        output = read(get_source(_CONFIG), _CONFIG, catalog)

        http_mocker.assert_number_of_calls(request, 1)

    assert [record.record.data[key] for record in output.records] == [item[key] for item in collection]
    assert not output.errors
