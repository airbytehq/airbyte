# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


CONFIG = {"api_token": "test-token"}
# Simplecast returns the whole lookup list in one response, has no paging info and ignores
# `offset`, so a paginated read would be served the same records forever. The mock caps that
# at MAX_REPEATS identical responses (then an empty one) so a regression fails instead of hanging.
MAX_REPEATS = 3


def _read(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"),
        config=CONFIG,
        catalog=catalog,
        state=[],
    )
    return read(source, config=CONFIG, catalog=catalog)


@pytest.mark.parametrize(
    "stream_name, records",
    [
        (
            "categories",
            [{"label": "Arts", "rss_label": "Arts"}, {"label": "Business", "rss_label": "Business"}, {"label": "Comedy", "rss_label": "Comedy"}],
        ),
        (
            "distribution_channels",
            [
                {"id": "apple", "name": "Apple Podcasts", "href": "https://api.simplecast.com/distribution_channels/apple"},
                {"id": "spotify", "name": "Spotify", "href": "https://api.simplecast.com/distribution_channels/spotify"},
                {"id": "youtube", "name": "YouTube", "href": "https://api.simplecast.com/distribution_channels/youtube"},
            ],
        ),
    ],
)
def test_unpaginated_lookup_stream_is_read_once(stream_name: str, records: list[dict]) -> None:
    calls = {"n": 0}

    def respond(request, context):
        calls["n"] += 1
        return {"collection": records if calls["n"] <= MAX_REPEATS else []}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"https://api.simplecast.com/{stream_name}", json=respond)
        output = _read(stream_name)

        assert output.errors == []
        assert [record.record.data for record in output.records] == records
        assert len(mocker.request_history) == 1
        request = mocker.request_history[0]
        assert request.path == f"/{stream_name}"
        assert request.qs == {}
        assert request.headers["Authorization"] == "Bearer test-token"
