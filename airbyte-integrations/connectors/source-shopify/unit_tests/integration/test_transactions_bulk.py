# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json
from datetime import datetime, timedelta
from typing import Any, Dict
from unittest import TestCase

from freezegun import freeze_time
from source_shopify import SourceShopify

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.integration.api.authentication import grant_all_scopes, set_up_shop
from unit_tests.integration.api.bulk import (
    JobCreationResponseBuilder,
    JobStatusResponseBuilder,
    create_job_creation_transactions_request,
    create_job_status_request,
)


_SHOP_NAME = "airbyte-integration-test"
_STREAM_NAME = "transactions"
_BULK_OPERATION_ID = "gid://shopify/BulkOperation/4472588009662"
_JOB_RESULT_URL = (
    "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/transactions-final"
    "?response-content-disposition=attachment%3B+filename%3D%22bulk-4476008693950.jsonl%22"
)

_STATE_VALUE = "2026-10-22T00:00:00+00:00"
_SLICE_START = datetime.fromisoformat(_STATE_VALUE)
_SLICE_END = _SLICE_START + timedelta(days=1)


def _config() -> Dict[str, Any]:
    return {
        "start_date": "2024-01-01",
        "shop": _SHOP_NAME,
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "bulk_window_in_days": 1,
    }


def _order_line(order_id: int, created_at: str, updated_at: str, transactions: list) -> str:
    return json.dumps(
        {
            "__typename": "Order",
            "id": f"gid://shopify/Order/{order_id}",
            "currency": "EUR",
            "order_created_at": created_at,
            "order_updated_at": updated_at,
            "transactions": transactions,
        }
    )


def _transaction(transaction_id: int, kind: str, status: str, created_at: str) -> Dict[str, Any]:
    return {
        "id": f"gid://shopify/OrderTransaction/{transaction_id}",
        "errorCode": None,
        "test": False,
        "kind": kind,
        "amount": "10.0",
        "createdAt": created_at,
        "status": status,
        "processedAt": created_at,
        "gateway": "shopify_payments",
        "paymentId": f"p{transaction_id}",
        "accountNumber": None,
        "formattedGateway": "Shopify Payments",
        "manuallyCapturable": False,
        "receipt": "{}",
        "parentTransaction": None,
        "authorization": None,
        "totalUnsettledSet": {"presentmentMoney": {"amount": "0.0", "currency": "EUR"}, "shopMoney": {"amount": "0.0", "currency": "EUR"}},
        "amountSet": {"shop_money": {"amount": "10.0", "currency": "EUR"}},
        "fees": [],
        "paymentDetails": {},
    }


@freeze_time(_SLICE_END)
class TransactionsBulkIncrementalTest(TestCase):
    def setUp(self) -> None:
        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()
        set_up_shop(self._http_mocker, _SHOP_NAME)
        grant_all_scopes(self._http_mocker, _SHOP_NAME)

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_incremental_read_emits_status_change_of_existing_refund_when_its_order_is_updated(self) -> None:
        self._http_mocker.post(
            create_job_creation_transactions_request(_SHOP_NAME, _SLICE_START, _SLICE_END),
            JobCreationResponseBuilder(job_created_at="2026-10-22T23:55:00Z").with_bulk_operation_id(_BULK_OPERATION_ID).build(),
        )
        self._http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
        )
        jsonl_lines = [
            # the order and both its transactions predate the state; the refund became SUCCESS afterwards, which updated the order
            _order_line(
                1,
                created_at="2026-10-20T08:00:00Z",
                updated_at="2026-10-22T15:10:00Z",
                transactions=[
                    _transaction(1001, "SALE", "SUCCESS", "2026-10-20T08:00:00Z"),
                    _transaction(1002, "REFUND", "SUCCESS", "2026-10-21T09:00:00Z"),
                ],
            ),
            # a new order with a new transaction
            _order_line(
                2,
                created_at="2026-10-22T12:00:00Z",
                updated_at="2026-10-22T12:00:05Z",
                transactions=[_transaction(2001, "SALE", "SUCCESS", "2026-10-22T12:00:00Z")],
            ),
        ]
        self._http_mocker.get(HttpRequest(_JOB_RESULT_URL), HttpResponse("\n".join(jsonl_lines) + "\n"))

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"created_at": _STATE_VALUE}).build()
        output = read(SourceShopify(), _config(), catalog, state=state)

        assert output.errors == []
        emitted = [(record.record.data["id"], record.record.data["status"]) for record in output.records]
        assert sorted(emitted) == [(1001, "SUCCESS"), (1002, "SUCCESS"), (2001, "SUCCESS")]
        assert all("order_updated_at" not in record.record.data for record in output.records)
        assert output.most_recent_state.stream_state.__dict__ == {"created_at": "2026-10-22T12:00:00+00:00"}
