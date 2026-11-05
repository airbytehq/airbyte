#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from itertools import islice
from pathlib import Path

import pytest
import requests_mock
import yaml

from airbyte_cdk.legacy.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource


@pytest.fixture
def streams(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> dict:
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    config = {"api_token": "test-token"}
    manifest = yaml.safe_load((Path(__file__).parents[1] / "manifest.yaml").read_text())
    source = ManifestDeclarativeSource(manifest, config=config)
    return {stream.name: stream for stream in source.streams(config)}


@pytest.mark.parametrize("stream_name", ["categories", "distribution_channels", "timezones"])
@pytest.mark.parametrize("record_count", [0, 1, 19])
def test_lookup_reads_once(streams: dict, requests_mock: requests_mock.Mocker, stream_name: str, record_count: int) -> None:
    records = [{"id": str(index), "value": str(index)} for index in range(record_count)]
    url = f"https://api.simplecast.com/{stream_name}"
    requests_mock.get(url, json={"href": url, "collection": records})

    emitted = list(
        islice(
            (record for partition in streams[stream_name].generate_partitions() for record in partition.read()),
            record_count + 1,
        )
    )

    assert [dict(record) for record in emitted] == records
    assert [request.url for request in requests_mock.request_history] == [url]


def test_analytics_reads_once_per_podcast(streams: dict, requests_mock: requests_mock.Mocker) -> None:
    requests_mock.get(
        "https://api.simplecast.com/podcasts/?offset=0", json={"collection": [{"id": "one"}, {"id": "two"}]}, complete_qs=True
    )
    requests_mock.get("https://api.simplecast.com/podcasts/?offset=2", json={"collection": []}, complete_qs=True)
    records = [
        {
            "href": f"https://api.simplecast.com/analytics?podcast={podcast}",
            "downloads": {"href": f"/analytics/downloads?podcast={podcast}"},
        }
        for podcast in ["one", "two"]
    ]
    for podcast, record in zip(["one", "two"], records):
        requests_mock.get(f"https://api.simplecast.com/analytics?podcast={podcast}", json=record)

    emitted = list(islice((record for partition in streams["analytics"].generate_partitions() for record in partition.read()), 3))

    assert [dict(record) for record in emitted] == records
    assert [request.url for request in requests_mock.request_history if "/analytics?" in request.url] == [
        "https://api.simplecast.com/analytics?podcast=one",
        "https://api.simplecast.com/analytics?podcast=two",
    ]


@pytest.mark.parametrize("stream_name", ["podcasts", "episodes"])
def test_list_streams_still_paginate(streams: dict, requests_mock: requests_mock.Mocker, stream_name: str) -> None:
    if stream_name == "episodes":
        requests_mock.get("https://api.simplecast.com/podcasts/?offset=0", json={"collection": [{"id": "parent"}]}, complete_qs=True)
        requests_mock.get("https://api.simplecast.com/podcasts/?offset=1", json={"collection": []}, complete_qs=True)
        url = "https://api.simplecast.com/podcasts/parent/episodes"
    else:
        url = "https://api.simplecast.com/podcasts/"
    for offset, records in [(0, [{"id": "first"}, {"id": "second"}]), (2, [{"id": "third"}]), (3, [])]:
        requests_mock.get(f"{url}?offset={offset}", json={"collection": records}, complete_qs=True)

    emitted = [record for partition in streams[stream_name].generate_partitions() for record in partition.read()]

    assert [record["id"] for record in emitted] == ["first", "second", "third"]
    assert [request.url for request in requests_mock.request_history if request.url.startswith(url + "?")] == [
        f"{url}?offset=0",
        f"{url}?offset=2",
        f"{url}?offset=3",
    ]
