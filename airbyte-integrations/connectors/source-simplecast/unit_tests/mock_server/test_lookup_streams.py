# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import requests
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


CONFIG = {"api_token": "test-token"}
pytestmark = pytest.mark.timeout(10)


@pytest.mark.parametrize("stream_name", ["categories", "distribution_channels"])
@pytest.mark.parametrize("ids", [["lookup-1", "lookup-2", "lookup-3"], []], ids=["nonempty", "empty"])
def test_lookup_stream_reads_once(stream_name, ids, monkeypatch):
    request = HttpRequest(url=f"https://api.simplecast.com/{stream_name}", query_params=ANY_QUERY_PARAMS)
    response = HttpResponse(body=json.dumps({"collection": [{"id": record_id} for record_id in ids]}))
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    requests_sent = []

    def bounded_send(session, prepared_request, **kwargs):
        requests_sent.append(prepared_request.url)
        assert len(requests_sent) <= 2, f"Lookup stream kept requesting pages: {requests_sent}"
        return send(session, prepared_request, **kwargs)

    with HttpMocker() as http_mocker:
        send = requests.Session.send
        monkeypatch.setattr(requests.Session, "send", bounded_send)
        http_mocker.get(request, [response, response])
        output = read(get_source(CONFIG), CONFIG, catalog)
        http_mocker.assert_number_of_calls(request, 1)

    assert [record.record.data["id"] for record in output.records] == ids
    assert not output.errors
