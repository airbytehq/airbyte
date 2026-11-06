# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest import TestCase

from freezegun import freeze_time
from source_shopify import SourceShopify
from source_shopify.shopify_graphql.bulk.query import ShopifyBulkTemplates, Transaction
from source_shopify.streams.base_streams import ShopifyStream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.integration.api.authentication import grant_all_scopes, set_up_shop
from unit_tests.integration.api.bulk import JobCreationResponseBuilder, JobStatusResponseBuilder, create_job_status_request


_SHOP_NAME = "airbyte-integration-test"
_STREAM = "transactions"
_BULK_OPERATION_ID = "gid://shopify/BulkOperation/4472588009661"
_URL_GRAPHQL = f"https://{_SHOP_NAME}.myshopify.com/admin/api/{ShopifyStream.api_version}/graphql.json"
_JOB_RESULT_URL = (
    "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/transactions-final"
    "?response-content-disposition=attachment%3B+filename%3D%22bulk-4476008693950.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-4476008693950.jsonl"
    "&response-content-type=application%2Fjsonl"
)

_STATE_VALUE = "2026-10-22T14:16:17+00:00"
_SYNC_TIME = "2026-10-22T15:01:00+00:00"


def _config() -> Dict[str, Any]:
    return {
        "start_date": "2025-01-01",
        "shop": _SHOP_NAME,
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "bulk_window_in_days": 1,
    }


def _job_creation_request(lower_boundary: str, upper_boundary: str) -> HttpRequest:
    query = Transaction(_config()).get("updated_at", lower_boundary, upper_boundary)
    return HttpRequest(url=_URL_GRAPHQL, body=json.dumps({"query": ShopifyBulkTemplates.prepare(query)}))


def _transaction(transaction_id: int, kind: str, status: str, created_at: str, parent_id: Optional[int] = None) -> Dict[str, Any]:
    return {
        "id": f"gid://shopify/OrderTransaction/{transaction_id}",
        "errorCode": None,
        "test": False,
        "kind": kind,
        "amount": "25.0",
        "createdAt": created_at,
        "status": status,
        "processedAt": created_at,
        "gateway": "shopify_payments",
        "paymentId": f"payment-{transaction_id}",
        "accountNumber": None,
        "formattedGateway": "Shopify Payments",
        "manuallyCapturable": False,
        "receipt": "{}",
        "parentTransaction": {"parentId": f"gid://shopify/OrderTransaction/{parent_id}"} if parent_id else None,
        "authorization": None,
        "totalUnsettledSet": {
            "presentmentMoney": {"amount": "0.0", "currency": "USD"},
            "shopMoney": {"amount": "0.0", "currency": "USD"},
        },
        "amountSet": {"shop_money": {"amount": "25.0", "currency": "USD"}},
        "fees": [],
        "paymentDetails": {},
    }


def _order_line(order_id: int, created_at: str, updated_at: str, transactions: List[Dict[str, Any]]) -> str:
    return json.dumps(
        {
            "__typename": "Order",
            "id": f"gid://shopify/Order/{order_id}",
            "currency": "USD",
            "order_created_at": created_at,
            "order_updated_at": updated_at,
            "transactions": transactions,
        }
    )


@freeze_time(_SYNC_TIME)
class TransactionsBulkIncrementalTest(TestCase):
    def setUp(self) -> None:
        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()
        set_up_shop(self._http_mocker, _SHOP_NAME)
        grant_all_scopes(self._http_mocker, _SHOP_NAME)

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_incremental_read_emits_status_change_of_transaction_created_before_state(self) -> None:
        """
        A refund created (PENDING) before the saved `created_at` state settles to SUCCESS afterwards.
        Shopify bumps the order's `updatedAt`, so the BULK job (filtered by orders `updated_at`) returns the order;
        the refund must be emitted again with its new status, even though its own `createdAt` predates the state.
        """
        self._http_mocker.post(
            _job_creation_request(_STATE_VALUE, _SYNC_TIME),
            JobCreationResponseBuilder(job_created_at="2026-10-22T15:01:00Z").with_bulk_operation_id(_BULK_OPERATION_ID).build(),
        )
        self._http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
        )
        jsonl = "\n".join(
            [
                # order created long before the state, updated after it when its refund settled
                _order_line(
                    1,
                    created_at="2026-10-20T09:00:00Z",
                    updated_at="2026-10-22T15:00:30Z",
                    transactions=[
                        _transaction(101, "SALE", "SUCCESS", "2026-10-20T09:00:05Z"),
                        _transaction(102, "REFUND", "SUCCESS", "2026-10-22T11:30:00Z", parent_id=101),
                    ],
                ),
                # a brand-new sale created after the state
                _order_line(
                    2,
                    created_at="2026-10-22T14:50:00Z",
                    updated_at="2026-10-22T14:50:10Z",
                    transactions=[_transaction(201, "SALE", "SUCCESS", "2026-10-22T14:50:05Z")],
                ),
            ]
        )
        self._http_mocker.get(HttpRequest(_JOB_RESULT_URL), HttpResponse(jsonl + "\n", status_code=200))

        state = StateBuilder().with_stream_state(_STREAM, {"created_at": _STATE_VALUE}).build()
        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
        output = read(SourceShopify(), _config(), catalog, state=state)

        assert output.errors == []
        records = {record.record.data["id"]: record.record.data for record in output.records}
        assert sorted(records) == [101, 102, 201]
        assert records[102]["status"] == "SUCCESS"
        assert records[102]["kind"] == "REFUND"
        assert records[102]["order_id"] == 1
        assert all("order_created_at" not in data and "order_updated_at" not in data for data in records.values())
        # the cursor keeps tracking the newest transaction `created_at`; re-emitted older transactions do not move it back
        assert output.most_recent_state.stream_state.__dict__ == {"created_at": "2026-10-22T14:50:05+00:00"}
