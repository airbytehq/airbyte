# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List

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
_JOB_RESULT_URL = (
    "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/transactions-final"
    "?response-content-disposition=attachment%3B+filename%3D%22bulk-4476008693949.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-4476008693949.jsonl"
    "&response-content-type=application%2Fjsonl"
)
_URL_GRAPHQL = f"https://{_SHOP_NAME}.myshopify.com/admin/api/{ShopifyStream.api_version}/graphql.json"

_STATE_VALUE = "2024-05-05T00:00:00+00:00"
_SYNC_TIME = datetime.fromisoformat(_STATE_VALUE) + timedelta(hours=24)


def _config() -> Dict[str, Any]:
    return {
        "start_date": "2022-05-05",
        "shop": _SHOP_NAME,
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "bulk_window_in_days": 1,
    }


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
        "paymentId": f"payment-{transaction_id}",
        "accountNumber": None,
        "formattedGateway": "Shopify Payments",
        "manuallyCapturable": False,
        "receipt": "{}",
        "parentTransaction": None,
        "authorization": None,
        "totalUnsettledSet": {
            "presentmentMoney": {"amount": "0.0", "currency": "EUR"},
            "shopMoney": {"amount": "0.0", "currency": "EUR"},
        },
        "amountSet": {"shop_money": {"amount": "10.0", "currency": "EUR"}},
        "fees": [],
        "paymentDetails": {},
    }


def _order(order_id: int, created_at: str, updated_at: str, transactions: List[Dict[str, Any]]) -> str:
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


@freeze_time(_SYNC_TIME)
def test_incremental_read_emits_status_change_of_transaction_created_before_state() -> None:
    jsonl = "\n".join(
        [
            # order and refund both predate the state; the refund turned SUCCESS after the state, which updated the order
            _order(
                1,
                created_at="2024-05-01T10:00:00Z",
                updated_at="2024-05-05T09:00:00Z",
                transactions=[
                    _transaction(101, "SALE", "SUCCESS", "2024-05-01T10:00:00Z"),
                    _transaction(102, "REFUND", "SUCCESS", "2024-05-04T12:00:00Z"),
                ],
            ),
            # order last updated before the state (eg returned because of the lookback window) -> already synced, not re-emitted
            _order(
                2,
                created_at="2024-05-02T10:00:00Z",
                updated_at="2024-05-04T23:00:00Z",
                transactions=[_transaction(201, "SALE", "SUCCESS", "2024-05-02T10:00:00Z")],
            ),
            # brand new transaction on an old order
            _order(
                3,
                created_at="2024-05-03T10:00:00Z",
                updated_at="2024-05-05T11:00:00Z",
                transactions=[_transaction(301, "REFUND", "PENDING", "2024-05-05T11:00:00Z")],
            ),
        ]
    )

    with HttpMocker() as http_mocker:
        set_up_shop(http_mocker, _SHOP_NAME)
        grant_all_scopes(http_mocker, _SHOP_NAME)
        # the BULK job is requested for orders updated since the saved `created_at` state
        job_creation_query = ShopifyBulkTemplates.prepare(Transaction(_config()).get("updated_at", _STATE_VALUE, _SYNC_TIME.isoformat()))
        http_mocker.post(
            HttpRequest(_URL_GRAPHQL, body=json.dumps({"query": job_creation_query})),
            JobCreationResponseBuilder(job_created_at=(_SYNC_TIME - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"))
            .with_bulk_operation_id(_BULK_OPERATION_ID)
            .build(),
        )
        http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
        )
        http_mocker.get(HttpRequest(_JOB_RESULT_URL), HttpResponse(jsonl + "\n", status_code=200))

        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
        state = StateBuilder().with_stream_state(_STREAM, {"created_at": _STATE_VALUE}).build()
        output = read(SourceShopify(), _config(), catalog, state=state)

    assert output.errors == []
    records = {record.record.data["id"]: record.record.data for record in output.records}
    # every transaction of an order updated since the state is re-emitted, so the refund's new status reaches the destination
    assert sorted(records) == [101, 102, 301]
    assert records[102]["status"] == "SUCCESS"
    assert all("order_updated_at" not in record and "order_created_at" not in record for record in records.values())
    # the order `updatedAt` must be requested, it is what makes the older transactions eligible for emission
    assert "order_updated_at: updatedAt" in job_creation_query
    # re-emitted older transactions do not move the cursor backwards
    assert output.most_recent_state.stream_state.created_at == "2024-05-05T11:00:00+00:00"
