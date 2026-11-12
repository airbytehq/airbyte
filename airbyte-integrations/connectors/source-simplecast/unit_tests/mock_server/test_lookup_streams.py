# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `categories` and `distribution_channels` lookup streams.

Both endpoints return their full list in a single response with no paging
information and ignore `offset`, so the connector must make exactly one
request and emit each value once.
"""

import json

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"api_token": "test-token"}
_BASE_URL = "https://api.simplecast.com"

_CATEGORIES = [{"value": f"category-{i}", "label": f"Category {i}", "rss_label": f"Category {i}"} for i in range(19)]
_DISTRIBUTION_CHANNELS = [
    {"id": f"channel-{i}", "name": f"Channel {i}", "href": f"{_BASE_URL}/distribution_channels/channel-{i}"} for i in range(5)
]


@pytest.mark.parametrize(
    "stream_name,path,records,id_field",
    [
        ("categories", "/categories", _CATEGORIES, "value"),
        ("distribution_channels", "/distribution_channels", _DISTRIBUTION_CHANNELS, "id"),
    ],
)
def test_lookup_stream_is_read_in_a_single_request(stream_name, path, records, id_field):
    # Only the un-paginated request is registered; any `?offset=N` request is
    # unmatched and fails the read.
    request = HttpRequest(url=f"{_BASE_URL}{path}", query_params={}, headers={"Authorization": "Bearer test-token"})
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"collection": records}), status_code=200))

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), _CONFIG, catalog)

        assert [record.record.data[id_field] for record in output.records] == [record[id_field] for record in records]
        assert not output.errors
        http_mocker.assert_number_of_calls(request, 1)
