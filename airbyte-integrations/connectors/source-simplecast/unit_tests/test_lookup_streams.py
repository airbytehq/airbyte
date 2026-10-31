# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the unpaginated Simplecast endpoints.

`/categories`, `/distribution_channels` and `/analytics` return their full
payload in one response and ignore `offset`. Offset pagination on these streams
never received an empty page, so syncs re-requested the same data forever and
emitted endless duplicates. These tests pin that each stream issues exactly one
request without an `offset` parameter: any `offset` request is unmocked and
fails the test.
"""

import json
from typing import Any, Dict, List
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_CONFIG = {"api_token": "token"}
_BASE_URL = "https://api.simplecast.com"
_PODCAST_ID = "podcast-1"


def _read(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog)


def _collection_response(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"collection": records}), status_code=200)


class TestCategoriesStream(TestCase):
    @HttpMocker()
    def test_single_request_without_offset(self, http_mocker: HttpMocker) -> None:
        categories = [{"label": f"Category {i}", "rss_label": f"cat-{i}", "value": f"cat-{i}"} for i in range(19)]
        response = _collection_response(categories)
        http_mocker.get(HttpRequest(f"{_BASE_URL}/categories", query_params={}), response)

        output = _read("categories")

        assert len(output.records) == 19
        assert [r.record.data["value"] for r in output.records] == [c["value"] for c in categories]


class TestDistributionChannelsStream(TestCase):
    @HttpMocker()
    def test_single_request_without_offset(self, http_mocker: HttpMocker) -> None:
        channels = [{"id": f"channel-{i}", "name": f"Channel {i}", "href": f"{_BASE_URL}/c/{i}"} for i in range(5)]
        response = _collection_response(channels)
        http_mocker.get(HttpRequest(f"{_BASE_URL}/distribution_channels", query_params={}), response)

        output = _read("distribution_channels")

        assert len(output.records) == 5
        assert [r.record.data["id"] for r in output.records] == [c["id"] for c in channels]


class TestAnalyticsStream(TestCase):
    @HttpMocker()
    def test_single_request_per_podcast_without_offset(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/podcasts/", query_params={"offset": "0"}),
            _collection_response([{"id": _PODCAST_ID, "title": "Podcast"}]),
        )
        http_mocker.get(HttpRequest(f"{_BASE_URL}/podcasts/", query_params={"offset": "1"}), _collection_response([]))
        analytics = HttpResponse(
            body=json.dumps({"id": _PODCAST_ID, "downloads": {"href": f"{_BASE_URL}/analytics/downloads"}}),
            status_code=200,
        )
        analytics_url = f"{_BASE_URL}/analytics"
        http_mocker.get(HttpRequest(analytics_url, query_params={"podcast": _PODCAST_ID}), analytics)

        output = _read("analytics")

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == _PODCAST_ID
