# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


CONFIG = {"api_token": "test-token"}
MANIFEST = Path(__file__).parents[2] / "manifest.yaml"


def _read(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST), config=CONFIG, catalog=catalog, state=[])
    return read(source, config=CONFIG, catalog=catalog)


@pytest.mark.parametrize(
    "stream_name, path, collection, key",
    [
        pytest.param(
            "categories",
            "categories",
            [{"value": f"cat-{i}", "label": f"Category {i}"} for i in range(19)],
            "value",
            id="categories",
        ),
        pytest.param(
            "distribution_channels",
            "distribution_channels",
            [{"id": f"dc-{i}", "name": f"Channel {i}"} for i in range(3)],
            "id",
            id="distribution_channels",
        ),
    ],
)
def test_unpaginated_lookup_stream_is_requested_once_and_emits_each_value_once(stream_name, path, collection, key):
    # Simplecast lookup endpoints ignore `offset` and return the full list every time,
    # with no paging information. Serve the full list on every request (bounded by an
    # empty third response so a regression terminates instead of looping forever).
    full_page = json.dumps({"collection": collection})
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"https://api.simplecast.com/{path}",
            [{"text": full_page}, {"text": full_page}, {"text": json.dumps({"collection": []})}],
        )
        output = _read(stream_name)
        history = mocker.request_history

    assert [record.record.data[key] for record in output.records] == [item[key] for item in collection]
    assert len(history) == 1
    assert history[0].path == f"/{path}"
    assert history[0].qs == {}
    assert history[0].headers["Authorization"] == "Bearer test-token"
