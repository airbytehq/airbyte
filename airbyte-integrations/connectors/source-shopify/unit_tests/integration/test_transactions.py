# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json
from datetime import datetime
from typing import Any, Dict, List

from freezegun import freeze_time
from source_shopify import SourceShopify
from source_shopify.shopify_graphql.bulk.query import ShopifyBulkTemplates, Transaction

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
_URL_GRAPHQL = f"https://{_SHOP_NAME}.myshopify.com/admin/api/2026-10/graphql.json"

_NOW = "2024-05-05T02:24:00+00:00"
_STATE_CREATED_AT = "2024-05-05T01:00:00+00:00"


def _config() -> Dict[str, Any]:
    return {
        "start_date": "2024-01-01",
        "shop": _SHOP_NAME,
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "bulk_window_in_days": 1,
    }


def _job_creation_request(start: str, end: str) -> HttpRequest:
    query = Transaction(_config()).get("updated_at", start, end)
    return HttpRequest(url=_URL_GRAPHQL, body=json.dumps({"query": ShopifyBulkTemplates.prepare(query)}))


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


@freeze_time(datetime.fromisoformat(_NOW))
def test_incremental_read_emits_transactions_of_orders_updated_since_state() -> None:
    """
    A refund created before the saved state that later changes from PENDING to SUCCESS updates its order,
    so the order is exported again by the BULK job. The refund's new status has to be emitted even though
    neither the refund nor the order were created after the saved state.
    """
    jsonl = "\n".join(
        [
            # order and its transactions were created before the state, the refund became SUCCESS after it
            _order(
                1,
                created_at="2024-05-04T10:00:00Z",
                updated_at="2024-05-05T01:30:00Z",
                transactions=[
                    _transaction(1001, "SALE", "SUCCESS", "2024-05-04T10:00:00Z"),
                    _transaction(1002, "REFUND", "SUCCESS", "2024-05-04T12:00:00Z"),
                ],
            ),
            # a brand new order and transaction, after the state
            _order(
                2,
                created_at="2024-05-05T02:00:00Z",
                updated_at="2024-05-05T02:00:00Z",
                transactions=[_transaction(2001, "SALE", "SUCCESS", "2024-05-05T02:00:00Z")],
            ),
        ]
    )

    with HttpMocker() as http_mocker:
        set_up_shop(http_mocker, _SHOP_NAME)
        grant_all_scopes(http_mocker, _SHOP_NAME)
        job_creation_request = _job_creation_request(_STATE_CREATED_AT, _NOW)
        http_mocker.post(job_creation_request, JobCreationResponseBuilder().with_bulk_operation_id(_BULK_OPERATION_ID).build())
        http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
        )
        http_mocker.get(HttpRequest(_JOB_RESULT_URL), HttpResponse(jsonl + "\n", status_code=200))

        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
        state = StateBuilder().with_stream_state(_STREAM, {"created_at": _STATE_CREATED_AT}).build()
        output = read(SourceShopify(), _config(), catalog, state=state)

        http_mocker.assert_number_of_calls(job_creation_request, 1)

    assert output.errors == []
    records = [message.record.data for message in output.records]
    assert sorted((record["id"], record["status"]) for record in records) == [
        (1001, "SUCCESS"),
        (1002, "SUCCESS"),
        (2001, "SUCCESS"),
    ]
    # helper fields used for the state comparison are not part of the output
    assert all("order_created_at" not in record and "order_updated_at" not in record for record in records)
    # the cursor only moves forward with newly created transactions
    assert output.most_recent_state.stream_state.__dict__["created_at"] == "2024-05-05T02:00:00+00:00"
