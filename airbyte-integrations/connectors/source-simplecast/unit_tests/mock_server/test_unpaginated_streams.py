# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


@pytest.mark.parametrize("stream_name,record_key", [("categories", "value"), ("distribution_channels", "id")])
@pytest.mark.parametrize("record_count", [3, 0])
def test_reads_collection_once(stream_name, record_key, record_count, monkeypatch):
    records = [{record_key: str(index), "label": f"Record {index}"} for index in range(record_count)]
    config = {"api_token": "test-token"}
    source = get_source(config)
    # Bound buggy pagination while every offset still returns the same full collection.
    monkeypatch.setattr(source._constructor, "_limit_pages_fetched_per_slice", 2)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    request = HttpRequest(url=f"https://api.simplecast.com/{stream_name}", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"collection": records}), status_code=200))

        output = read(source, config=config, catalog=catalog)

        assert [message.record.data for message in output.records] == records
        assert [message.record.data[record_key] for message in output.records] == [record[record_key] for record in records]
        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("stream_name", ["categories", "distribution_channels"])
def test_http_error_fails_read(stream_name):
    config = {"api_token": "test-token"}
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    request = HttpRequest(url=f"https://api.simplecast.com/{stream_name}", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"error": "Unauthorized"}), status_code=401))

        output = read(get_source(config), config=config, catalog=catalog, expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(request, 1)
