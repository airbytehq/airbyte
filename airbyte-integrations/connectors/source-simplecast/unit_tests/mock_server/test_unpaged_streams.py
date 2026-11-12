# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


@pytest.mark.parametrize("stream_name", ["categories", "distribution_channels"])
@pytest.mark.parametrize("record_count", [3, 0])
def test_unpaged_list_is_read_once(stream_name, record_count):
    records = [{"id": f"id-{index}", "value": f"value-{index}"} for index in range(record_count)]
    config = {"api_token": "test-token"}
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    request = HttpRequest(f"https://api.simplecast.com/{stream_name}", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as http_mocker:
        full_list = HttpResponse(json.dumps({"collection": records}))
        # Two identical full lists reproduce an offset-ignoring endpoint. A terminal
        # error bounds the unfixed sync; a correct sync never requests it.
        http_mocker.get(request, [full_list, full_list, HttpResponse("{}", status_code=401)])
        output = read(get_source(config, catalog), config=config, catalog=catalog)

        http_mocker.assert_number_of_calls(request, 1)
        assert sorted(record.record.data["id"] for record in output.records) == sorted(record["id"] for record in records)
        assert not output.errors
