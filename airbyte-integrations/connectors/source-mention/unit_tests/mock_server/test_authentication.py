# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from ..conftest import get_source


@pytest.mark.parametrize("stream", ["account_me", "alert"])
@pytest.mark.parametrize("status", [200, 401])
@pytest.mark.parametrize("empty", [False, True])
def test_bearer_authentication(stream: str, status: int, empty: bool) -> None:
    config = {"api_key": "test-key", "stats_start_date": "2026-01-01T00:00:00Z"}
    headers = {"Authorization": "Bearer test-key"}
    account_request = HttpRequest("https://api.mention.net/api/accounts/me", headers=headers)
    payload = {"account": {"id": "account-id"}}
    if empty and stream == "account_me":
        payload = {"account": []}
    if status == 401:
        payload = {"error": "invalid_token"}
    with HttpMocker() as mocker:
        mocker.get(account_request, HttpResponse(json.dumps(payload), status))
        if stream == "alert" and status == 200:
            alert_request = HttpRequest(
                "https://api.mention.net/api/accounts/account-id/alerts",
                headers=headers,
                query_params={"limit": "100"},
            )
            mocker.get(alert_request, HttpResponse(json.dumps({"alerts": [] if empty else [{"id": "alert-id"}], "_links": {}}), 200))
        output = read(
            get_source(config),
            config,
            CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build(),
            expecting_exception=status == 401,
        )
        if status == 401:
            assert output.errors
            assert not output.records
        else:
            assert not output.errors
            assert [message.record.data["id"] for message in output.records] == (
                [] if empty else [f"{'account' if stream == 'account_me' else 'alert'}-id"]
            )
        mocker.assert_number_of_calls(account_request, 1)
