# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_CONFIG = {"api_token": "test-token"}
_BASE_URL = "https://api.simplecast.com"


def _categories_records():
    return [{"value": f"cat-{i}", "label": f"Category {i}", "rss_label": f"Category {i}"} for i in range(19)]


def _distribution_channels_records():
    return [{"id": f"dc-{i}", "name": f"Channel {i}", "href": f"{_BASE_URL}/distribution_channels/dc-{i}"} for i in range(5)]


def _response(records):
    # Simplecast lookup endpoints return the whole list in one response with no paging info,
    # and ignore any `offset` query parameter.
    return HttpResponse(body=json.dumps({"collection": records}), status_code=200)


def _read(stream_name):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog)


@pytest.mark.parametrize(
    "stream_name, path, records, id_field",
    [
        ("categories", "/categories", _categories_records(), "value"),
        ("distribution_channels", "/distribution_channels", _distribution_channels_records(), "id"),
    ],
)
def test_lookup_stream_reads_full_list_once_without_offset_pagination(stream_name, path, records, id_field):
    """The API returns the full lookup list on every call regardless of `offset`, so the stream must
    issue exactly one request and emit each value exactly once."""
    with HttpMocker() as http_mocker:
        request = HttpRequest(url=f"{_BASE_URL}{path}", query_params=ANY_QUERY_PARAMS)
        # If the connector paginates, it gets the full list again and then an empty page
        # (which ends an otherwise endless loop so the test fails instead of hanging).
        http_mocker.get(
            request,
            [_response(records), _response(records), _response([])],
        )

        output = _read(stream_name)

        emitted_ids = [r.record.data[id_field] for r in output.records]
        assert emitted_ids == [r[id_field] for r in records]
        assert not any(log.log.level == "ERROR" for log in output.logs)
        http_mocker.assert_number_of_calls(request, 1)
