# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def test_account_me_sends_bearer_token():
    with HttpMocker() as http_mocker:
        config = {"api_key": "test-api-key", "stats_start_date": "2026-01-01T00:00:00Z"}
        request = HttpRequest(
            url="https://api.mention.net/api/accounts/me",
            headers={"Authorization": "Bearer test-api-key"},
        )
        http_mocker.get(request, HttpResponse(body=json.dumps({"account": {"id": "account-1"}}), status_code=200))
        catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()

        output = read(get_source(config), config=config, catalog=catalog)

        assert [message.record.data["id"] for message in output.records] == ["account-1"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)
