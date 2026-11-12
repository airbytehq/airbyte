# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS

from ..conftest import get_source


@pytest.mark.parametrize(
    "stream,records",
    [
        (
            "categories",
            [
                {"value": "arts", "label": "Arts", "rss_label": "Arts"},
                {"value": "business", "label": "Business", "rss_label": "Business"},
                {"value": "comedy", "label": "Comedy", "rss_label": "Comedy"},
            ],
        ),
        (
            "distribution_channels",
            [
                {"id": "apple", "name": "Apple Podcasts", "href": "https://podcasts.apple.com"},
                {"id": "spotify", "name": "Spotify", "href": "https://open.spotify.com"},
                {"id": "amazon", "name": "Amazon Music", "href": "https://music.amazon.com"},
            ],
        ),
    ],
)
@pytest.mark.parametrize("empty", [False, True])
def test_read_unpaginated_collection(stream: str, records: list[dict], empty: bool) -> None:
    records = [] if empty else records
    config = {"api_token": "test-token"}
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    request = HttpRequest(f"https://api.simplecast.com/{stream}", query_params=ANY_QUERY_PARAMS)
    response = HttpResponse(json.dumps({"collection": records}), 200)

    with HttpMocker() as mocker:
        # Ignore offset like the API, but stop after two full responses to bound a broken paginator.
        mocker.get(request, [response, response, HttpResponse(json.dumps({"collection": []}), 200)])
        output = read(get_source(config), config, catalog)

        mocker.assert_number_of_calls(request, 1)
        assert [message.record.data for message in output.records] == records
        assert output.errors == []


@pytest.mark.parametrize("stream", ["categories", "distribution_channels"])
def test_read_authentication_error(stream: str) -> None:
    config = {"api_token": "test-token"}
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    request = HttpRequest(f"https://api.simplecast.com/{stream}", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as mocker:
        mocker.get(request, HttpResponse(json.dumps({"error": "Unauthorized"}), 401))
        output = read(get_source(config), config, catalog, expecting_exception=True)

        mocker.assert_number_of_calls(request, 1)
        assert output.records == []
        assert output.errors
