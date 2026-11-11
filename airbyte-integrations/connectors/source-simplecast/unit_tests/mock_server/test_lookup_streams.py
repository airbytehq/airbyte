# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import re

import pytest
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


@pytest.mark.parametrize(
    "stream_name,records",
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
                {"id": "apple_podcasts", "name": "Apple Podcasts", "href": "https://podcasts.apple.com"},
                {"id": "spotify", "name": "Spotify", "href": "https://open.spotify.com"},
            ],
        ),
    ],
)
@pytest.mark.parametrize("empty", [False, True], ids=["populated", "empty"])
def test_lookup_read_completes_without_pagination(
    source: YamlDeclarativeSource, requests_mock: Mocker, stream_name: str, records: list[dict], empty: bool
) -> None:
    url = f"https://api.simplecast.com/{stream_name}"
    expected_records = [] if empty else records
    response = {"collection": expected_records}
    # Repeat the full list regardless of offset, then bound a regressed read with an empty response.
    requests_mock.get(
        re.compile(rf"^{re.escape(url)}(?:\?.*)?$"),
        [{"json": response}] * 3 + [{"json": {"collection": []}}],
    )
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    output = read(source, config={"api_token": "test-token"}, catalog=catalog)

    assert [message.record.data for message in output.records] == expected_records
    assert [request.url for request in requests_mock.request_history] == [url]
