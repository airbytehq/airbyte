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

# The lookup endpoints return their whole list in one response, carry no paging information and
# ignore `offset`/`limit`. The safety cap only keeps a paginating connector from looping forever here.
SAFETY_CAP = 5

LOOKUPS = {
    "categories": (
        "value",
        [
            {"value": "arts", "label": "Arts", "rss_label": "Arts", "subcategories": {"collection": []}},
            {"value": "business", "label": "Business", "rss_label": "Business", "subcategories": {"collection": []}},
            {"value": "comedy", "label": "Comedy", "rss_label": "Comedy", "subcategories": {"collection": []}},
        ],
    ),
    "distribution_channels": (
        "id",
        [
            {"id": "960dcb10", "name": "Apple Podcasts", "href": f"{URL_BASE}/distribution_channels/960dcb10"},
            {"id": "00512816", "name": "Google Podcasts", "href": f"{URL_BASE}/distribution_channels/00512816"},
            {"id": "bb916df4", "name": "Spotify", "href": f"{URL_BASE}/distribution_channels/bb916df4"},
        ],
    ),
}


@pytest.mark.parametrize("stream_name", sorted(LOOKUPS))
def test_lookup_stream_is_read_in_one_request_and_emits_each_value_once(stream_name: str) -> None:
    key, collection = LOOKUPS[stream_name]
    url = f"{URL_BASE}/{stream_name}"

    def full_list_whatever_the_offset(request, context) -> dict:
        over_cap = mocker.call_count > SAFETY_CAP
        return {"href": url, "collection": [] if over_cap else collection}

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"), config=CONFIG, catalog=catalog, state=[]
    )
    with requests_mock.Mocker() as mocker:
        mocker.get(url, json=full_list_whatever_the_offset)
        output = read(source, config=CONFIG, catalog=catalog)

    assert [record.record.data[key] for record in output.records] == [item[key] for item in collection]
    assert [(request.path, request.qs) for request in mocker.request_history] == [(f"/{stream_name}", {})]
    assert mocker.request_history[0].headers["Authorization"] == "Bearer test-token"
    assert output.errors == []
