# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {"api_token": "test_token"}
_URL_BASE = "https://api.simplecast.com"

# These endpoints return their whole payload in one response and ignore `offset`/`limit`.
# The mocks imitate that by answering identically whatever the query string is. A real
# endpoint never returns an empty page, so the trailing empty response exists only to
# make a connector that keeps paging terminate, letting the test fail instead of hang.
_REPEATS_BEFORE_EMPTY = 3


def _read(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog)


def _requests_to(mocker: requests_mock.Mocker, path: str):
    return [request for request in mocker.request_history if request.path == path]


@pytest.mark.parametrize(
    "stream_name, path, id_field, collection",
    [
        pytest.param(
            "categories",
            "/categories",
            "value",
            [{"value": "arts", "label": "Arts"}, {"value": "business", "label": "Business"}, {"value": "comedy", "label": "Comedy"}],
            id="categories",
        ),
        pytest.param(
            "distribution_channels",
            "/distribution_channels",
            "id",
            [{"id": "apple", "name": "Apple Podcasts"}, {"id": "spotify", "name": "Spotify"}, {"id": "overcast", "name": "Overcast"}],
            id="distribution_channels",
        ),
    ],
)
def test_lookup_stream_is_requested_once_and_emits_each_value_once(stream_name, path, id_field, collection):
    full_list = {"href": f"{_URL_BASE}{path}", "collection": collection}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_URL_BASE}{path}", [{"json": full_list}] * _REPEATS_BEFORE_EMPTY + [{"json": {"collection": []}}])
        output = _read(stream_name)

    assert [record.record.data[id_field] for record in output.records] == [item[id_field] for item in collection]
    assert [request.query for request in _requests_to(mocker, path)] == [""]
    assert output.errors == []


def test_analytics_emits_one_record_per_podcast():
    podcast_ids = ["podcast-1", "podcast-2"]

    def analytics(podcast_id: str) -> dict:
        return {
            "href": f"{_URL_BASE}/analytics?podcast={podcast_id}",
            "downloads": {"href": f"{_URL_BASE}/analytics/downloads?podcast={podcast_id}"},
        }

    with requests_mock.Mocker() as mocker:
        # `podcasts` is a real paginated list: the page past the end is empty.
        mocker.get(f"{_URL_BASE}/podcasts/?offset=0", json={"collection": [{"id": podcast_id} for podcast_id in podcast_ids]})
        mocker.get(f"{_URL_BASE}/podcasts/?offset=2", json={"collection": []})
        for podcast_id in podcast_ids:
            mocker.get(
                f"{_URL_BASE}/analytics?podcast={podcast_id}",
                [{"json": analytics(podcast_id)}] * _REPEATS_BEFORE_EMPTY + [{"json": {}}],
            )
        output = _read("analytics")

    assert sorted(record.record.data["href"] for record in output.records) == [
        analytics(podcast_id)["href"] for podcast_id in podcast_ids
    ]
    assert sorted(request.query for request in _requests_to(mocker, "/analytics")) == ["podcast=podcast-1", "podcast=podcast-2"]
    assert output.errors == []
