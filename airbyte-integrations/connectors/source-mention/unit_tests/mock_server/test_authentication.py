# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import List

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ConfigBuilder


_API_KEY = "test_api_key"
_BASE_URL = "https://api.mention.net/api"
_ACCOUNT_ID = "account-1"


def _authorized_request(path: str) -> HttpRequest:
    return HttpRequest(url=f"{_BASE_URL}{path}", headers={"Authorization": f"Bearer {_API_KEY}"})


def _mock_account_me(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        _authorized_request("/accounts/me"),
        HttpResponse(body=json.dumps({"account": {"id": _ACCOUNT_ID, "name": "Test Account"}}), status_code=200),
    )


def _mock_alerts(http_mocker: HttpMocker) -> None:
    http_mocker.get(
        HttpRequest(
            url=f"{_BASE_URL}/accounts/{_ACCOUNT_ID}/alerts",
            query_params={"limit": "100"},
            headers={"Authorization": f"Bearer {_API_KEY}"},
        ),
        HttpResponse(body=json.dumps({"alerts": [{"id": "alert-1"}, {"id": "alert-2"}], "_links": {}}), status_code=200),
    )


@pytest.mark.parametrize(
    "stream_name, mocks, expected_ids",
    [
        pytest.param("account_me", [_mock_account_me], [_ACCOUNT_ID], id="account_me"),
        pytest.param("alert", [_mock_account_me, _mock_alerts], ["alert-1", "alert-2"], id="alert_substream"),
    ],
)
def test_read_sends_api_key_as_bearer_token(stream_name: str, mocks: List, expected_ids: List[str]) -> None:
    config = ConfigBuilder().with_api_key(_API_KEY).build()
    with HttpMocker() as http_mocker:
        for mock in mocks:
            mock(http_mocker)

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(config=config), config=config, catalog=catalog)

    assert [record.record.data["id"] for record in output.records] == expected_ids
    assert not output.errors
