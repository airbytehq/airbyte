# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


class TestAccountMe(TestCase):
    @HttpMocker()
    def test_read_uses_bearer_authentication(self, http_mocker: HttpMocker):
        config = {"api_key": "test-api-key", "stats_start_date": "2026-01-01T00:00:00Z"}
        request = HttpRequest(
            url="https://api.mention.net/api/accounts/me",
            headers={"Authorization": f"Bearer {config['api_key']}"},
        )
        http_mocker.get(
            request,
            HttpResponse(body=json.dumps({"account": {"id": "account-123", "name": "Test account"}}), status_code=200),
        )

        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build(),
        )

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["account-123"]
        http_mocker.assert_number_of_calls(request, 1)
