# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("stream_name,key,count", [("categories", "value", 19), ("distribution_channels", "id", 5)])
def test_lookup_stream_reads_collection_once(stream_name: str, key: str, count: int) -> None:
    config = {"api_token": "test-token"}
    records = [{key: str(index)} for index in range(count)]
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    request = HttpRequest(
        url=f"https://api.simplecast.com/{stream_name}",
        query_params={},
        headers={"Authorization": "Bearer test-token"},
    )

    with HttpMocker() as http:
        http.get(request, HttpResponse(body=json.dumps({"collection": records}), status_code=200))

        output = read(get_source(config), config, catalog)

        assert not output.errors
        assert [message.record.data for message in output.records] == records
        http.assert_number_of_calls(request, 1)
