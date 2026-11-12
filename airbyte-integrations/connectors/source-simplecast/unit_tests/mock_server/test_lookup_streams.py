# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


MANIFEST_PATH = Path(__file__).parents[2] / "manifest.yaml"
CONFIG = {"api_token": "test-token"}

CATEGORIES = [{"value": f"category-{i}", "label": f"Category {i}", "rss_label": f"Category {i}"} for i in range(19)]
DISTRIBUTION_CHANNELS = [
    {"id": f"channel-{i}", "name": f"Channel {i}", "href": f"https://api.simplecast.com/distribution_channels/channel-{i}"}
    for i in range(6)
]


@pytest.mark.parametrize(
    "stream_name, records, record_key",
    [
        pytest.param("categories", CATEGORIES, "value", id="categories"),
        pytest.param("distribution_channels", DISTRIBUTION_CHANNELS, "id", id="distribution_channels"),
    ],
)
def test_unpaginated_lookup_stream_is_read_once(stream_name: str, records: list[dict], record_key: str) -> None:
    # The Simplecast lookup endpoints ignore `offset` and return the full list on every call.
    # The trailing empty page only bounds the read if the connector wrongly keeps paginating.
    url = f"https://api.simplecast.com/{stream_name}"
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), config=CONFIG, catalog=catalog, state=None)

    with requests_mock.Mocker() as mocker:
        mocker.get(
            url,
            [
                {"json": {"collection": records}},
                {"json": {"collection": records}},
                {"json": {"collection": []}},
            ],
        )
        output = read(source, config=CONFIG, catalog=catalog)
        history = mocker.request_history

    assert [record.record.data[record_key] for record in output.records] == [record[record_key] for record in records]
    assert [request.url for request in history] == [url]
    assert history[0].headers["Authorization"] == "Bearer test-token"
