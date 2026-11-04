# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


MANIFEST = Path(__file__).parents[1] / "manifest.yaml"
if not MANIFEST.exists():
    MANIFEST = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
CONFIG = {"api_token": "test-token"}
BASE_URL = "https://api.simplecast.com"


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


def read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST), config=CONFIG, catalog=catalog)
    return read(source, CONFIG, catalog)


@pytest.mark.parametrize("stream_name,record_count", [("categories", 19), ("distribution_channels", 2), ("timezones", 3)])
@pytest.mark.parametrize("empty", [False, True])
def test_lookup_stream_reads_collection_once(stream_name: str, record_count: int, empty: bool) -> None:
    records = [] if empty else [{"id": str(index), "value": str(index), "label": f"Lookup {index}"} for index in range(record_count)]
    with Mocker() as http:

        def unpaginated_response(request, context) -> dict:
            assert http.call_count <= 3, "Lookup endpoint keeps returning the same collection regardless of offset"
            return {"collection": records}

        http.get(f"{BASE_URL}/{stream_name}", json=unpaginated_response, request_headers={"Authorization": "Bearer test-token"})
        output = read_stream(stream_name)

    assert http.call_count == 1, [request.url for request in http.request_history]
    assert http.request_history[0].qs == {}
    assert not output.errors
    actual_records = []
    for message in output.records:
        assert message.record is not None
        actual_records.append(message.record.data)
    assert actual_records == records


@pytest.mark.parametrize("stream_name", ["podcasts", "episodes"])
def test_paginated_streams_still_read_all_pages(stream_name: str) -> None:
    path = "/podcasts/" if stream_name == "podcasts" else "/podcasts/parent/episodes"
    with Mocker() as http:
        if stream_name == "episodes":
            http.get(f"{BASE_URL}/podcasts/?offset=0", json={"collection": [{"id": "parent"}]}, complete_qs=True)
            http.get(f"{BASE_URL}/podcasts/?offset=1", json={"collection": []}, complete_qs=True)
        first = http.get(f"{BASE_URL}{path}?offset=0", json={"collection": [{"id": "first"}, {"id": "second"}]}, complete_qs=True)
        second = http.get(f"{BASE_URL}{path}?offset=2", json={"collection": [{"id": "third"}]}, complete_qs=True)
        last = http.get(f"{BASE_URL}{path}?offset=3", json={"collection": []}, complete_qs=True)
        output = read_stream(stream_name)

    assert not output.errors
    actual_ids = []
    for message in output.records:
        assert message.record is not None
        actual_ids.append(message.record.data["id"])
    assert actual_ids == ["first", "second", "third"]
    assert first.call_count == second.call_count == last.call_count == 1
