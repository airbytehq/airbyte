# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


def test_read_sends_api_key_as_bearer_token() -> None:
    config = {"api_key": "test-mention-key", "stats_start_date": "2026-01-01T00:00:00Z"}
    request = HttpRequest(
        url="https://api.mention.net/api/accounts/me",
        headers={"Authorization": "Bearer test-mention-key"},
    )
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()

    with HttpMocker() as http:
        http.get(request, HttpResponse(json.dumps({"account": {"id": "123", "name": "Test account"}}), 200))

        output = read(get_source(config), config, catalog)

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["123"]
        http.assert_number_of_calls(request, 1)
