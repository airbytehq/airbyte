# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


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
                {"id": "apple", "name": "Apple Podcasts", "href": "https://podcasts.apple.com/"},
                {"id": "spotify", "name": "Spotify", "href": "https://open.spotify.com/"},
                {"id": "amazon", "name": "Amazon Music", "href": "https://music.amazon.com/"},
            ],
        ),
    ],
)
@pytest.mark.parametrize("response_kind", ["collection", "empty", "error"])
def test_single_request(stream: str, records: list[dict], response_kind: str) -> None:
    config = {"api_token": "fixture-token"}
    expected = records if response_kind == "collection" else []
    response = HttpResponse(
        json.dumps({"collection": expected} if response_kind != "error" else {"message": "Unauthorized"}),
        401 if response_kind == "error" else 200,
    )
    target = HttpRequest(f"https://api.simplecast.com/{stream}", query_params={})
    with HttpMocker() as http:
        http.get(target, response)
        # Bound the broken paginator while retaining duplicate records as regression evidence.
        offset_requests = []
        for offset in (0, len(records), 2 * len(records)):
            request = HttpRequest(f"https://api.simplecast.com/{stream}", query_params={"offset": str(offset)})
            offset_requests.append(request)
            http.get(request, HttpResponse('{"collection": []}', 200) if offset == 2 * len(records) else response)

        output = read(get_source(config), config, CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build())

        assert [record.record.data for record in output.records] == expected
        assert bool(output.errors) == (response_kind == "error")
        http.assert_number_of_calls(target, 1)
        for request in offset_requests:
            http.assert_number_of_calls(request, 0)
