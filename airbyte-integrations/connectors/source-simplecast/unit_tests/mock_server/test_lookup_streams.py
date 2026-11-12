# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from conftest import get_source


_CONFIG = {"api_token": "test-token"}
_URL_BASE = "https://api.simplecast.com"


@pytest.mark.parametrize(
    "stream_name,path,records,id_field",
    [
        pytest.param(
            "categories",
            "/categories",
            [
                {"label": "Arts", "rss_label": "Arts"},
                {"label": "Business", "rss_label": "Business"},
                {"label": "Comedy", "rss_label": "Comedy"},
            ],
            "label",
            id="categories",
        ),
        pytest.param(
            "distribution_channels",
            "/distribution_channels",
            [
                {"id": "dc1", "name": "Apple Podcasts"},
                {"id": "dc2", "name": "Spotify"},
                {"id": "dc3", "name": "Google Podcasts"},
            ],
            "id",
            id="distribution_channels",
        ),
    ],
)
def test_lookup_stream_is_read_in_a_single_unpaginated_request(stream_name, path, records, id_field):
    """
    The Simplecast lookup endpoints return the full list in one response and ignore `offset`.
    The mock mirrors that: every request, whatever its query, gets the full list. The connector
    must send exactly one request without an `offset` parameter and emit each value exactly once.
    """
    with requests_mock.Mocker() as mocker:
        # The trailing empty page only exists so a paginating connector terminates in the test;
        # against the real API that behaviour loops until the attempt times out.
        mocker.get(
            f"{_URL_BASE}{path}",
            [{"json": {"collection": records}}] * 3 + [{"json": {"collection": []}}],
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

    assert [r.record.data[id_field] for r in output.records] == [r[id_field] for r in records]
    assert [(req.path, req.qs) for req in mocker.request_history] == [(path, {})]
    assert not any(log.log.level == "ERROR" for log in output.logs)
