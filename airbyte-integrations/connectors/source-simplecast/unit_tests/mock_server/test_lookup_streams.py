# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_CONFIG = {"api_token": "test-token"}
_URL_BASE = "https://api.simplecast.com"


def _categories(count):
    return [{"value": f"category-{i}", "label": f"Category {i}", "rss_label": f"Category {i}"} for i in range(count)]


def _distribution_channels(count):
    return [{"id": f"channel-{i}", "name": f"Channel {i}", "href": f"{_URL_BASE}/distribution_channels/channel-{i}"} for i in range(count)]


def _collection_response(records):
    # Simplecast lookup endpoints return the whole list in one response, with no paging information.
    return HttpResponse(json.dumps({"collection": records}), 200)


@pytest.mark.parametrize(
    "stream_name, path, records, record_key",
    [
        pytest.param("categories", "/categories", _categories(19), "value", id="categories"),
        pytest.param("distribution_channels", "/distribution_channels", _distribution_channels(5), "id", id="distribution_channels"),
    ],
)
def test_lookup_stream_reads_the_full_list_once_without_offset_paging(stream_name, path, records, record_key):
    """
    The lookup endpoints ignore `offset` and always return the full list. The connector must issue a single
    request and emit each value exactly once instead of re-requesting the endpoint with increasing offsets.
    """
    request = HttpRequest(url=f"{_URL_BASE}{path}", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as http_mocker:
        # The API returns the same full list regardless of `offset`; the trailing empty response only bounds
        # the read if the connector (incorrectly) keeps paging, so the test fails instead of hanging.
        http_mocker.get(
            request,
            [_collection_response(records), _collection_response(records), _collection_response([])],
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), _CONFIG, catalog)

        assert [record.record.data[record_key] for record in output.records] == [record[record_key] for record in records]
        http_mocker.assert_number_of_calls(request, 1)
        assert not output.errors
