# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs, urlparse

import pytest
from conftest import get_source
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


CONFIG = {"api_token": "test-token"}
BASE_URL = "https://api.simplecast.com"


@pytest.mark.parametrize(
    "stream_name,records",
    [
        ("categories", [{"value": "arts", "label": "Arts"}, {"value": "business", "label": "Business"}]),
        ("distribution_channels", [{"id": "apple", "name": "Apple Podcasts"}, {"id": "spotify", "name": "Spotify"}]),
        ("timezones", [{"value": "America/Los_Angeles"}, {"value": "Europe/London"}]),
    ],
)
def test_lookup_emits_collection_once(stream_name: str, records: list[dict], requests_mock: Mocker) -> None:
    url = f"{BASE_URL}/{stream_name}"
    # Repeat the offset-ignoring response, then stop the unfixed connector instead of hanging the suite.
    requests_mock.get(url, [{"json": {"collection": records}}, {"json": {"collection": records}}, {"json": {"collection": []}}])
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    output = read(get_source(CONFIG, catalog), CONFIG, catalog)

    assert [request.url for request in requests_mock.request_history] == [url]
    assert [message.record.data for message in output.records] == records
    assert not output.errors


def test_analytics_emits_one_object_per_podcast(requests_mock: Mocker) -> None:
    podcasts = [{"id": "podcast-one"}, {"id": "podcast-two"}]
    requests_mock.get(f"{BASE_URL}/podcasts/?offset=0", json={"collection": podcasts}, complete_qs=True)
    requests_mock.get(f"{BASE_URL}/podcasts/?offset=2", json={"collection": []}, complete_qs=True)
    analytics = [{"downloads": {"total": 10}}, {"downloads": {"total": 20}}]
    for podcast, record in zip(podcasts, analytics):
        requests_mock.get(
            f"{BASE_URL}/analytics?podcast={podcast['id']}",
            # An empty response after two repeats bounds the pre-fix infinite loop.
            [{"json": record}, {"json": record}, {"json": []}],
        )
    catalog = CatalogBuilder().with_stream("analytics", SyncMode.full_refresh).build()

    output = read(get_source(CONFIG, catalog), CONFIG, catalog)

    requests = [request for request in requests_mock.request_history if urlparse(request.url).path == "/analytics"]
    assert [request.qs for request in requests] == [{"podcast": ["podcast-one"]}, {"podcast": ["podcast-two"]}]
    assert [message.record.data for message in output.records] == analytics
    assert not output.errors


@pytest.mark.parametrize("stream_name", ["podcasts", "episodes"])
def test_collection_pagination_keeps_all_pages(stream_name: str, requests_mock: Mocker) -> None:
    if stream_name == "episodes":
        requests_mock.get(f"{BASE_URL}/podcasts/?offset=0", json={"collection": [{"id": "parent"}]}, complete_qs=True)
        requests_mock.get(f"{BASE_URL}/podcasts/?offset=1", json={"collection": []}, complete_qs=True)
    path = "/podcasts/" if stream_name == "podcasts" else "/podcasts/parent/episodes"
    records = [{"id": "first"}, {"id": "second"}, {"id": "third"}]
    for offset, page in [(0, records[:2]), (2, records[2:]), (3, [])]:
        requests_mock.get(f"{BASE_URL}{path}?offset={offset}", json={"collection": page}, complete_qs=True)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    output = read(get_source(CONFIG, catalog), CONFIG, catalog)

    requests = [request for request in requests_mock.request_history if urlparse(request.url).path == path]
    assert [parse_qs(urlparse(request.url).query) for request in requests] == [{"offset": ["0"]}, {"offset": ["2"]}, {"offset": ["3"]}]
    assert [message.record.data["id"] for message in output.records] == ["first", "second", "third"]
    assert not output.errors
