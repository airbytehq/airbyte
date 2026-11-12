# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


@pytest.mark.parametrize(
    "stream_name,records",
    [
        ("categories", [{"value": "arts"}, {"value": "business"}, {"value": "comedy"}]),
        ("distribution_channels", [{"id": "apple"}, {"id": "spotify"}, {"id": "amazon"}]),
    ],
)
@pytest.mark.parametrize("empty", [False, True])
def test_read_emits_collection_once(stream_name: str, records: list[dict], empty: bool, http_mocker: HttpMocker):
    records = [] if empty else records
    url = f"https://api.simplecast.com/{stream_name}"
    request = HttpRequest(url)
    paginated_requests = [HttpRequest(url, query_params={"offset": offset}) for offset in ("0", "3")]
    response = HttpResponse(json.dumps({"collection": records}))
    http_mocker.get(request, response)
    # Bound the broken paginator to two full pages; a third request is unmatched.
    for paginated_request in paginated_requests:
        http_mocker.get(paginated_request, response)

    config = {"api_token": "test-token"}
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(config), config=config, catalog=catalog)

    assert [record.record.data for record in output.records] == records
    assert output.errors == []
    http_mocker.assert_number_of_calls(request, 1)
    for paginated_request in paginated_requests:
        http_mocker.assert_number_of_calls(paginated_request, 0)


@pytest.mark.parametrize("stream_name", ["categories", "distribution_channels"])
def test_read_reports_http_error(stream_name: str, http_mocker: HttpMocker):
    request = HttpRequest(f"https://api.simplecast.com/{stream_name}", query_params=ANY_QUERY_PARAMS)
    http_mocker.get(request, HttpResponse('{"error": "Unauthorized"}', status_code=401))
    config = {"api_token": "test-token"}
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    output = read(get_source(config), config=config, catalog=catalog, expecting_exception=True)

    assert output.records == []
    assert output.errors
    http_mocker.assert_number_of_calls(request, 1)
