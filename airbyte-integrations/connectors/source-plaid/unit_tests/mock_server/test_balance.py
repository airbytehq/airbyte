# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import BASE_URL, ConfigBuilder, credentials_body


@freezegun.freeze_time("2026-01-15T12:00:00Z")
class TestBalance(TestCase):
    @HttpMocker()
    def test_balance_flattens_balances_and_drops_account_metadata(self, http_mocker: HttpMocker) -> None:
        body = {**credentials_body(), "options": {"min_last_updated_datetime": "2026-01-01T00:00:00Z"}}
        account = {
            "account_id": "acc-1",
            "balances": {
                "available": 100.0,
                "current": 110.0,
                "iso_currency_code": "USD",
                "limit": 500.0,
                "unofficial_currency_code": "XTS",
            },
            "mask": "0000",
            "name": "Plaid Checking",
            "official_name": "Plaid Gold Standard 0% Interest Checking",
            "subtype": "checking",
            "type": "depository",
        }
        http_mocker.post(
            HttpRequest(url=f"{BASE_URL}/accounts/balance/get", body=body),
            HttpResponse(body=json.dumps({"accounts": [account]}), status_code=200),
        )

        config = ConfigBuilder().with_start_date("2026-01-01").build()
        catalog = CatalogBuilder().with_stream("balance", SyncMode.full_refresh).build()
        output = read(get_source(config=config), config=config, catalog=catalog)

        assert [record.record.data for record in output.records] == [
            {
                "account_id": "acc-1",
                "available": 100.0,
                "current": 110.0,
                "iso_currency_code": "USD",
                "limit": 500.0,
                "unofficial_currency_code": "XTS",
            }
        ]
