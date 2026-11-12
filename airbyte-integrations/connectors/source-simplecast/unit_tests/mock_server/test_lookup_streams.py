# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_token": "test-token"}
MANIFEST = Path(__file__).parents[2] / "manifest.yaml"


def categories(count: int) -> list[dict]:
    return [{"value": f"category-{i}", "label": f"Category {i}", "rss_label": f"Category {i}"} for i in range(count)]


def distribution_channels(count: int) -> list[dict]:
    return [
        {"id": f"channel-{i}", "name": f"Channel {i}", "href": f"https://api.simplecast.com/distribution_channels/channel-{i}"}
        for i in range(count)
    ]


@pytest.mark.parametrize(
    "stream_name, records, key",
    [
        pytest.param("categories", categories(19), "value", id="categories"),
        pytest.param("distribution_channels", distribution_channels(5), "id", id="distribution_channels"),
    ],
)
def test_lookup_stream_reads_full_list_in_one_request(stream_name: str, records: list[dict], key: str) -> None:
    # Simplecast returns the whole lookup list in one response without paging info and ignores `offset`.
    request = HttpRequest(f"https://api.simplecast.com/{stream_name}", query_params={})
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST), config=CONFIG, catalog=catalog, state=[])

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps({"collection": records})))
        output = read(source, config=CONFIG, catalog=catalog)
        http_mocker.assert_number_of_calls(request, 1)

    assert [r.record.data[key] for r in output.records] == [record[key] for record in records]
    assert not output.errors
