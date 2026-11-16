# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Offset pagination contract shared by every stream (all six use the same paginator)."""

import json
from typing import Any, Dict, List

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://api.postmarkapp.com"
_PAGE_SIZE = 500
_SERVER_TOKEN = "test-server-token"
_ACCOUNT_TOKEN = "test-account-token"
_CONFIG = {"X-Postmark-Server-Token": _SERVER_TOKEN, "X-Postmark-Account-Token": _ACCOUNT_TOKEN}
_SERVER_AUTH = {"X-Postmark-Server-Token": _SERVER_TOKEN}
_ACCOUNT_AUTH = {"X-Postmark-Account-Token": _ACCOUNT_TOKEN}

# stream name, API path, records key in the response, primary key, auth header
_STREAMS = [
    ("deliverystats", "/deliverystats", "Bounces", "Name", _SERVER_AUTH),
    ("message-streams", "/message-streams", "MessageStreams", "ID", _SERVER_AUTH),
    ("messages", "/messages/outbound", "Messages", "ID", _SERVER_AUTH),
    ("bounces", "/bounces", "Bounces", "ID", _SERVER_AUTH),
    ("domains", "/domains", "Domains", "ID", _ACCOUNT_AUTH),
    ("servers", "/servers", "Servers", "ID", _ACCOUNT_AUTH),
]


def _request(path: str, offset: int, headers: Dict[str, str]) -> HttpRequest:
    return HttpRequest(
        url=f"{_BASE_URL}{path}",
        query_params={"offset": str(offset), "count": str(_PAGE_SIZE)},
        headers=headers,
        body={"Accept": "application/json"},
    )


def _response(records_key: str, primary_key: str, ids: List[str]) -> HttpResponse:
    body: Dict[str, Any] = {records_key: [{primary_key: record_id} for record_id in ids], "TotalCount": 1002}
    return HttpResponse(body=json.dumps(body), status_code=200)


@pytest.mark.parametrize("stream_name,path,records_key,primary_key,auth", _STREAMS, ids=[s[0] for s in _STREAMS])
def test_full_refresh_requests_each_offset_once_from_zero_and_stops_on_short_page(stream_name, path, records_key, primary_key, auth):
    pages = [
        [f"{stream_name}-{i}" for i in range(0, 500)],
        [f"{stream_name}-{i}" for i in range(500, 1000)],
        [f"{stream_name}-{i}" for i in range(1000, 1002)],
    ]
    with HttpMocker() as http_mocker:
        requests = [_request(path, offset, auth) for offset in (0, 500, 1000)]
        for request, ids in zip(requests, pages):
            http_mocker.get(request, _response(records_key, primary_key, ids))

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(config=_CONFIG), _CONFIG, catalog)

        assert not output.errors
        assert [record.record.data[primary_key] for record in output.records] == [record_id for page in pages for record_id in page]
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)
