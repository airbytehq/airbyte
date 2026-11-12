# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


def test_account_me_uses_bearer_authentication(http_mocker):
    config = {"api_key": "test_api_key", "stats_start_date": "2026-09-01T00:00:00Z"}
    request = HttpRequest(
        url="https://api.mention.net/api/accounts/me",
        headers={"Authorization": "Bearer test_api_key"},
    )
    http_mocker.get(request, HttpResponse(body=json.dumps({"account": {"id": "acc_1"}})))
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()

    output = read(get_source(config), config, catalog)

    assert http_mocker._mocker.request_history[0].headers["Authorization"] == "Bearer test_api_key"
    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["acc_1"]
    http_mocker.assert_number_of_calls(request, 1)
