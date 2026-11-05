# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


@pytest.mark.parametrize("stream_name, key", [("categories", "value"), ("distribution_channels", "id")])
@pytest.mark.parametrize("record_count", [3, 0])
def test_reads_collection_once_without_offset(stream_name, key, record_count):
    records = [{key: str(index), "label" if key == "value" else "name": f"Record {index}"} for index in range(record_count)]
    config = {"api_token": "test-api-token"}
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    request = HttpRequest(url=f"https://api.simplecast.com/{stream_name}")

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"collection": records}), status_code=200))

        output = read(get_source(config), config=config, catalog=catalog, state=StateBuilder().build())

        assert output.errors == [], output.errors
        assert [message.record.data for message in output.records] == records
        assert [message.record.data[key] for message in output.records] == [record[key] for record in records]
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("stream_name", ["categories", "distribution_channels"])
def test_api_error_is_not_silently_ignored(stream_name):
    config = {"api_token": "test-api-token"}
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    request = HttpRequest(url=f"https://api.simplecast.com/{stream_name}")

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"message": "Unauthorized"}), status_code=401))

        output = read(get_source(config), config=config, catalog=catalog, state=StateBuilder().build())

        assert output.errors
        assert output.records == []
        http_mocker.assert_number_of_calls(request, 1)
