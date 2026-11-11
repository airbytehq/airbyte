# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source
from mock_server.config import get_config

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("stream_name,record_key", [("categories", "value"), ("distribution_channels", "id")])
def test_full_list_is_read_once(stream_name, record_key):
    config = get_config()
    records = [{record_key: str(index)} for index in range(3)]
    request = HttpRequest(
        url=f"https://api.simplecast.com/{stream_name}",
        query_params={},
        headers={"Authorization": "Bearer test-token"},
    )
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"collection": records}), status_code=200))
        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build(),
        )
        assert [message.record.data for message in output.records] == records
        http_mocker.assert_number_of_calls(request, 1)
        assert not output.errors
