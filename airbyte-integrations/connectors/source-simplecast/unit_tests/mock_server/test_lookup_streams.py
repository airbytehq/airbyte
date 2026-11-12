# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from unit_tests.conftest import get_source


CONFIG = {"api_token": "test-token"}

LOOKUP_STREAMS = {
    "categories": [
        {"label": "Arts", "rss_label": "Arts", "subcategories": {"collection": []}},
        {"label": "Business", "rss_label": "Business", "subcategories": {"collection": []}},
        {"label": "Comedy", "rss_label": "Comedy", "subcategories": {"collection": []}},
    ],
    "distribution_channels": [
        {"id": "apple", "name": "Apple Podcasts", "href": "https://api.simplecast.com/distribution_channels/apple"},
        {"id": "spotify", "name": "Spotify", "href": "https://api.simplecast.com/distribution_channels/spotify"},
        {"id": "google", "name": "Google Podcasts", "href": "https://api.simplecast.com/distribution_channels/google"},
    ],
}


@pytest.mark.parametrize("stream_name", sorted(LOOKUP_STREAMS))
def test_unpaginated_lookup_stream_is_fetched_once_and_emits_each_value_once(stream_name: str) -> None:
    """
    Simplecast lookup endpoints return the whole list in one response, with no paging
    information, and ignore `offset`. The connector must request the endpoint exactly once
    (without an `offset` parameter) and emit every value exactly once.

    The mock keeps answering with the full list (the real API behaviour) and only returns an
    empty page on the third call, so a connector that wrongly paginates would emit duplicates
    instead of looping forever inside the test.
    """
    collection = LOOKUP_STREAMS[stream_name]
    url = f"https://api.simplecast.com/{stream_name}"
    with requests_mock.Mocker() as mocker:
        mocker.get(
            url,
            [
                {"json": {"collection": collection}},
                {"json": {"collection": collection}},
                {"json": {"collection": []}},
            ],
        )
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(CONFIG), CONFIG, catalog)

    sent = [request for request in mocker.request_history if request.path == f"/{stream_name}"]
    assert [request.qs for request in sent] == [{}]
    assert sent[0].headers["Authorization"] == "Bearer test-token"
    assert [record.record.data for record in output.records] == collection
    assert not output.errors
