# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


@pytest.mark.parametrize("stream,key,count", [("categories", "value", 19), ("distribution_channels", "id", 4)])
@pytest.mark.parametrize("empty", [False, True], ids=["full_collection", "empty_collection"])
def test_non_paginated_stream_reads_collection_once(stream, key, count, empty):
    config = {"api_token": "test-token"}
    records = [] if empty else [{key: str(index), "name" if key == "id" else "label": f"Item {index}"} for index in range(count)]
    request = HttpRequest(url=f"https://api.simplecast.com/{stream}", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as http_mocker:
        full_response = HttpResponse(body=json.dumps({"collection": records}), status_code=200)
        empty_response = HttpResponse(body=json.dumps({"collection": []}), status_code=200)
        http_mocker.get(request, [full_response, full_response, empty_response])

        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build(),
        )

        assert not output.errors
        assert len(output.records) == len(records)
        assert [record.record.data[key] for record in output.records] == [record[key] for record in records]
        assert [record.record.data for record in output.records] == records
        assert len({record.record.data[key] for record in output.records}) == len(records)
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("stream", ["categories", "distribution_channels"])
def test_non_paginated_stream_reports_authentication_error(stream):
    config = {"api_token": "test-token"}
    request = HttpRequest(url=f"https://api.simplecast.com/{stream}")
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"message": "Unauthorized"}), status_code=401))

        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build(),
        )

        assert output.errors
        assert not output.records
        http_mocker.assert_number_of_calls(request, 1)
