# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ADVERTISER_ID, BASE_URL, ConfigBuilder


@pytest.mark.parametrize(
    "stream, request_, body, primary_key",
    [
        pytest.param(
            "publishers",
            HttpRequest(url=f"{BASE_URL}/advertisers/{ADVERTISER_ID}/publishers"),
            [{"id": 1, "name": "Publisher 1", "salesRegions": ["GB"]}, {"id": 2, "name": "Publisher 2", "salesRegions": []}],
            "id",
            id="publishers",
        ),
        pytest.param(
            "accounts",
            HttpRequest(url=f"{BASE_URL}/accounts", query_params={"type": "advertiser"}),
            {
                "userId": 99,
                "accounts": [
                    {"accountId": 1, "accountName": "Advertiser 1", "accountType": "advertiser", "userRole": "admin"},
                    {"accountId": 2, "accountName": "Advertiser 2", "accountType": "advertiser", "userRole": "user"},
                ],
            },
            "accountId",
            id="accounts",
        ),
    ],
)
def test_full_refresh_read_emits_every_record(stream: str, request_: HttpRequest, body, primary_key: str) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(request_, HttpResponse(body=json.dumps(body), status_code=200))
        config = ConfigBuilder().build()
        catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()

        output = read(get_source(config=config, catalog=catalog), config, catalog)

    assert not output.errors
    assert [record.record.data[primary_key] for record in output.records] == [1, 2]
