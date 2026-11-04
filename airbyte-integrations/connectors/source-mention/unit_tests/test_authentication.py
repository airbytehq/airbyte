# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"api_key": "test-api-key", "stats_start_date": "2026-09-01T00:00:00Z"}
_ACCOUNTS_ME_REQUEST = HttpRequest(
    "https://api.mention.net/api/accounts/me",
    headers={"Authorization": "Bearer test-api-key"},
)
_ALERT_REQUEST = HttpRequest(
    "https://api.mention.net/api/accounts/acc_1/alerts",
    query_params={"limit": "100"},
    headers={"Authorization": "Bearer test-api-key"},
)


def _read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)


class AuthenticationTest(TestCase):
    @HttpMocker()
    def test_account_me_uses_bearer_authentication(self, http_mocker: HttpMocker):
        http_mocker.get(
            _ACCOUNTS_ME_REQUEST,
            HttpResponse(body=json.dumps({"account": {"id": "acc_1", "name": "Test Account"}}), status_code=200),
        )

        output = _read_stream("account_me")

        assert output.errors == []
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "acc_1"

    @HttpMocker()
    def test_alert_uses_bearer_authentication(self, http_mocker: HttpMocker):
        http_mocker.get(
            _ACCOUNTS_ME_REQUEST,
            HttpResponse(body=json.dumps({"account": {"id": "acc_1", "name": "Test Account"}}), status_code=200),
        )
        http_mocker.get(
            _ALERT_REQUEST,
            HttpResponse(body=json.dumps({"alerts": [{"id": 1, "name": "Alert 1"}], "_links": {}}), status_code=200),
        )

        output = _read_stream("alert")

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == [1]
