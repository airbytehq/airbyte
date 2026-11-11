# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS

from ..conftest import get_source


@pytest.mark.parametrize(
    "stream_name,record_key,record_count",
    [("categories", "value", 19), ("distribution_channels", "id", 5)],
)
def test_unpaginated_stream_is_requested_once(stream_name, record_key, record_count, monkeypatch):
    config = {"api_token": "test-token"}
    records = [{record_key: str(index)} for index in range(record_count)]
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    request = HttpRequest(f"https://api.simplecast.com/{stream_name}", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as mocker:
        mocker.get(request, HttpResponse(json.dumps({"collection": records})))
        send = requests.Session.send
        request_count = 0

        def bounded_send(session, prepared_request, **kwargs):
            nonlocal request_count
            request_count += 1
            assert request_count <= 2, "Unpaginated endpoint requested more than twice"
            return send(session, prepared_request, **kwargs)

        monkeypatch.setattr(requests.Session, "send", bounded_send)
        output = read(get_source(config), config, catalog)

        assert [message.record.data for message in output.records] == records
        assert output.errors == []
        mocker.assert_number_of_calls(request, 1)
        assert request_count == 1
