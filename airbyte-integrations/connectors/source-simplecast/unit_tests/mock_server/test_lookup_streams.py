# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


CONFIG = {"api_token": "test-token"}
URL_BASE = "https://api.simplecast.com"

CATEGORIES = [
    {"value": "arts", "rss_label": "Arts", "label": "Arts", "subcategories": {"collection": []}},
    {"value": "business", "rss_label": "Business", "label": "Business", "subcategories": {"collection": []}},
    {"value": "comedy", "rss_label": "Comedy", "label": "Comedy", "subcategories": {"collection": []}},
]
DISTRIBUTION_CHANNELS = [
    {"id": "960dcb10", "name": "Apple Podcasts", "href": f"{URL_BASE}/distribution_channels/960dcb10"},
    {"id": "00512816", "name": "Google Podcasts", "href": f"{URL_BASE}/distribution_channels/00512816"},
    {"id": "bb916df4", "name": "Spotify", "href": f"{URL_BASE}/distribution_channels/bb916df4"},
]

# The mocked server stops answering with data after this many requests, so that a connector
# that keeps paging fails the assertions below instead of hanging the test run.
_MAX_FULL_RESPONSES = 5


@pytest.mark.parametrize(
    "stream_name, key, collection",
    [
        pytest.param("categories", "value", CATEGORIES, id="categories"),
        pytest.param("distribution_channels", "id", DISTRIBUTION_CHANNELS, id="distribution_channels"),
    ],
)
def test_lookup_stream_is_read_with_one_request_and_no_duplicates(stream_name: str, key: str, collection: list[dict]) -> None:
    """The lookup endpoints return their whole list on every call and ignore `offset`."""
    url = f"{URL_BASE}/{stream_name}"

    def whole_list_whatever_the_offset(request, context) -> dict:
        served = collection if len(mocker.request_history) <= _MAX_FULL_RESPONSES else []
        return {"href": url, "collection": served}

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"),
        config=CONFIG,
        catalog=catalog,
        state=[],
    )
    with requests_mock.Mocker() as mocker:
        mocker.get(url, json=whole_list_whatever_the_offset)
        output = read(source, config=CONFIG, catalog=catalog)

    assert [record.record.data[key] for record in output.records] == [item[key] for item in collection]
    assert [request.url for request in mocker.request_history] == [url]
    assert mocker.request_history[0].headers["Authorization"] == "Bearer test-token"
    assert output.errors == []
