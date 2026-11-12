# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


def _collection_response(records):
    return HttpResponse(body=json.dumps({"collection": records}), status_code=200)


@pytest.mark.parametrize("stream_name,record_count", [("categories", 19), ("distribution_channels", 5)])
@pytest.mark.parametrize("empty", [False, True])
def test_lookup_collection_is_read_once(stream_name, record_count, empty):
    records = [] if empty else [{"id": str(index), "name": f"Lookup {index}"} for index in range(record_count)]
    config = {"api_token": "test-token"}
    # Lookup endpoints ignore pagination parameters; accept any to expose repeated reads.
    request = HttpRequest(f"https://api.simplecast.com/{stream_name}", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as http_mocker:
        # The final empty response bounds a regressed paginator instead of hanging the test.
        http_mocker.get(request, [_collection_response(records), _collection_response(records), _collection_response([])])
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(config), config=config, catalog=catalog)

        assert [record.record.data["id"] for record in output.records] == [record["id"] for record in records]
        http_mocker.assert_number_of_calls(request, 1)
        assert not output.errors

