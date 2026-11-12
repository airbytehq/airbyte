# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections.abc import Callable

import pytest
from requests_mock import Mocker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


@pytest.mark.parametrize(
    "stream_name, records",
    [
        (
            "categories",
            [
                {"value": value, "label": value.replace("_", " ").title(), "subcategories": {"collection": []}}
                for value in (
                    "arts",
                    "business",
                    "comedy",
                    "education",
                    "fiction",
                    "government",
                    "health_and_fitness",
                    "history",
                    "kids_and_family",
                    "leisure",
                    "music",
                    "news",
                    "religion_and_spirituality",
                    "science",
                    "society_and_culture",
                    "sports",
                    "tv_and_film",
                    "technology",
                    "true_crime",
                )
            ],
        ),
        (
            "distribution_channels",
            [
                {"id": "960dcb10-8203-4acc-8462-1868c84b0554", "name": "Apple Podcasts"},
                {"id": "00512816-1bf2-4828-9f69-5f6fcb3f68f6", "name": "Google Podcasts"},
                {"id": "bb916df4-9575-4c49-972e-b4a0966c078f", "name": "Spotify"},
            ],
        ),
    ],
    ids=["categories", "distribution_channels"],
)
def test_lookup_read_emits_collection_once(
    requests_mock: Mocker,
    get_source: Callable[[dict[str, str]], YamlDeclarativeSource],
    stream_name: str,
    records: list[dict[str, object]],
) -> None:
    config = {"api_token": "test-token"}
    url = f"https://api.simplecast.com/{stream_name}"

    def response(request: object, context: object) -> dict[str, object]:
        # The API ignores offsets. Bound the broken paginator so regressions fail without hanging.
        return {"href": url, "collection": records if requests_mock.call_count <= 3 else []}

    requests_mock.get(url, json=response)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config=config, catalog=catalog)

    assert not output.errors
    assert [message.record.data for message in output.records] == records, [request.url for request in requests_mock.request_history]
    assert [request.url for request in requests_mock.request_history] == [url]
    assert requests_mock.last_request.headers["Authorization"] == "Bearer test-token"
