# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def test_account_me_sends_bearer_token(source, config):
    account = {"id": "account-1"}
    with HttpMocker() as http_mocker:
        request = HttpRequest(
            url="https://api.mention.net/api/accounts/me",
            headers={"Authorization": "Bearer test-api-key"},
        )
        http_mocker.get(
            request,
            HttpResponse(body=json.dumps({"account": account})),
        )
        output = read(source, config, CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build())
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    assert [message.record.data["id"] for message in output.records] == ["account-1"]
