# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ADVERTISER_ID, BASE_URL, ConfigBuilder


_STREAM = "transactions"


def _transaction(transaction_id: int, commission_status: str) -> dict:
    return {
        "id": transaction_id,
        "advertiserId": int(ADVERTISER_ID),
        "publisherId": 777,
        "commissionStatus": commission_status,
        "transactionDate": "2024-01-02T10:00:00",
        "basketProducts": [{"productId": f"sku-{transaction_id}", "quantity": 2}],
    }


@freezegun.freeze_time("2024-01-03T12:00:00Z")
class TestTransactionsStream(TestCase):
    @HttpMocker()
    def test_requests_basket_products_and_marks_deleted_transactions(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                url=f"{BASE_URL}/advertisers/{ADVERTISER_ID}/transactions/",
                query_params={
                    "startDate": "2024-01-01T00:00:00",
                    "endDate": "2024-01-03T12:00:00",
                    "showBasketProducts": "true",
                },
            ),
            HttpResponse(
                body=json.dumps([_transaction(1, "approved"), _transaction(2, "deleted"), _transaction(3, "pending")]),
                status_code=200,
            ),
        )
        config = ConfigBuilder().build()
        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.full_refresh).build()

        output = read(get_source(config=config, catalog=catalog), config, catalog)

        assert not output.errors
        records = {record.record.data["id"]: record.record.data for record in output.records}
        assert {transaction_id: data["is_deleted"] for transaction_id, data in records.items()} == {
            1: False,
            2: True,
            3: False,
        }
        assert records[2]["basketProducts"] == [{"productId": "sku-2", "quantity": 2}]
