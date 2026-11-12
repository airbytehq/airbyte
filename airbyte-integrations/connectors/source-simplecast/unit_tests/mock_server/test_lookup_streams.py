# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


CONFIG = {"api_token": "test-token"}
MANIFEST_PATH = Path(__file__).parents[2] / "manifest.yaml"

# Trimmed copies of what the live endpoints return. Neither response carries paging information.
CATEGORIES = [
    {"value": "arts", "rss_label": "Arts", "label": "Arts", "subcategories": {"collection": []}},
    {"value": "business", "rss_label": "Business", "label": "Business", "subcategories": {"collection": []}},
    {"value": "comedy", "rss_label": "Comedy", "label": "Comedy", "subcategories": {"collection": []}},
]
DISTRIBUTION_CHANNELS = [
    {"id": "channel-1", "name": "Apple Podcasts", "href": "https://api.simplecast.com/distribution_channels/channel-1"},
    {"id": "channel-2", "name": "Google Podcasts", "href": "https://api.simplecast.com/distribution_channels/channel-2"},
    {"id": "channel-3", "name": "Spotify", "href": "https://api.simplecast.com/distribution_channels/channel-3"},
]
# The API would repeat the list forever. The mock stops after this many responses so a
# connector that keeps asking for further pages fails the assertions instead of hanging.
MAX_FULL_RESPONSES = 3


@pytest.mark.parametrize(
    ("stream_name", "collection"),
    [
        pytest.param("categories", CATEGORIES, id="categories"),
        pytest.param("distribution_channels", DISTRIBUTION_CHANNELS, id="distribution_channels"),
    ],
)
def test_lookup_stream_is_read_once_when_api_ignores_offset(stream_name: str, collection: list[dict]) -> None:
    url = f"https://api.simplecast.com/{stream_name}"

    def whole_list_whatever_the_offset(request, context) -> dict:
        served = len(mocker.request_history)
        return {"href": url, "collection": collection if served <= MAX_FULL_RESPONSES else []}

    with requests_mock.Mocker() as mocker:
        mocker.get(url, json=whole_list_whatever_the_offset)
        source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=CONFIG, catalog=None, state=None)
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(source, CONFIG, catalog)
        requests_sent = [(request.path, request.query) for request in mocker.request_history]

    assert [record.record.data for record in output.records] == collection
    assert requests_sent == [(f"/{stream_name}", "")]
    assert output.errors == []
