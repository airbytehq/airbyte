# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


CONFIG = {"api_token": "test-token"}
API_BASE = "https://api.simplecast.com"
# Safety cap so a connector that keeps paginating terminates instead of hanging the test.
MAX_SERVED_PAGES = 3


def _categories() -> List[Dict[str, Any]]:
    return [{"label": f"Category {i}", "rss_label": f"category-{i}", "subcategories": {"collection": []}} for i in range(19)]


def _distribution_channels() -> List[Dict[str, Any]]:
    return [{"id": f"channel-{i}", "name": f"Channel {i}", "href": f"{API_BASE}/distribution_channels/channel-{i}"} for i in range(5)]


@pytest.mark.parametrize(
    "stream_name, collection, key",
    [
        pytest.param("categories", _categories(), "label", id="categories"),
        pytest.param("distribution_channels", _distribution_channels(), "id", id="distribution_channels"),
    ],
)
def test_lookup_stream_reads_full_list_once_without_paginating(stream_name: str, collection: List[Dict[str, Any]], key: str) -> None:
    """
    Simplecast returns the whole lookup list in one response and ignores `offset`, with no paging info.
    The connector must issue a single request and emit each value exactly once.
    """

    def respond(request, context):
        # Mirrors the real API: every call returns the full list regardless of `offset`.
        # After MAX_SERVED_PAGES calls an empty page is served so a looping connector still terminates.
        if mocker.call_count > MAX_SERVED_PAGES:
            return {"collection": []}
        return {"collection": collection}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{API_BASE}/{stream_name}", json=respond)
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(CONFIG), CONFIG, catalog)

        history = mocker.request_history

    assert [record.record.data[key] for record in output.records] == [item[key] for item in collection]
    assert len(history) == 1
    assert history[0].qs == {}
    assert not output.errors
