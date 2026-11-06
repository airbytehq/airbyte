# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("account", [{"id": "account-123"}, {}], ids=["record", "empty"])
def test_read_account_me_sends_bearer_token(account):
    config = {"api_key": "test-api-key", "stats_start_date": "2026-01-01T00:00:00Z"}
    request = HttpRequest(
        url="https://api.mention.net/api/accounts/me",
        headers={"Authorization": "Bearer test-api-key"},
    )
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"account": account}), status_code=200))

        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build(),
        )

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == (["account-123"] if account else [])
        http_mocker.assert_number_of_calls(request, 1)


def test_read_account_me_reports_invalid_token():
    config = {"api_key": "invalid-api-key", "stats_start_date": "2026-01-01T00:00:00Z"}
    request = HttpRequest(
        url="https://api.mention.net/api/accounts/me",
        headers={"Authorization": "Bearer invalid-api-key"},
    )
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"error": "invalid_token"}), status_code=401))

        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build(),
        )

        assert output.records == []
        assert output.errors
        assert any("invalid_token" in error.trace.error.message for error in output.errors)
        http_mocker.assert_number_of_calls(request, 1)
