# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_token": "test-token"}

CATEGORIES = [{"label": f"Category {i}", "rss_label": f"category-{i}", "value": f"category_{i}"} for i in range(19)]
DISTRIBUTION_CHANNELS = [
    {"id": f"channel-{i}", "name": f"Channel {i}", "href": f"https://api.simplecast.com/distribution_channels/channel-{i}"}
    for i in range(5)
]


def read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"),
        config=CONFIG,
        catalog=catalog,
        state=None,
    )
    return read(source, config=CONFIG, catalog=catalog)


@pytest.mark.parametrize(
    ("stream_name", "collection", "record_key"),
    [
        pytest.param("categories", CATEGORIES, "value", id="categories"),
        pytest.param("distribution_channels", DISTRIBUTION_CHANNELS, "id", id="distribution_channels"),
    ],
)
def test_lookup_stream_reads_full_list_once_without_offset(
    http_mocker: HttpMocker, stream_name: str, collection: list[dict], record_key: str
) -> None:
    # The Simplecast lookup endpoints ignore `offset` and return the full list with no paging info,
    # so the stream must issue exactly one request with no query params and emit each value once.
    request = HttpRequest(f"https://api.simplecast.com/{stream_name}", query_params={})
    http_mocker.get(request, HttpResponse(json.dumps({"collection": collection}), 200))

    output = read_stream(stream_name)

    assert [record.record.data[record_key] for record in output.records] == [item[record_key] for item in collection]
    http_mocker.assert_number_of_calls(request, 1)
