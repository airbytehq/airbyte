# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json
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
_JOB_RESULT_URL = "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/transactions-final?response-content-disposition=attachment%3B+filename%3D%22bulk-4472588009661.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-4472588009661.jsonl&response-content-type=application%2Fjsonl"
_URL_GRAPHQL = f"https://{_SHOP_NAME}.myshopify.com/admin/api/{ShopifyStream.api_version}/graphql.json"

_STATE_CREATED_AT = "2024-05-04T23:16:17+00:00"
# the mocked BULK Job is created at 2024-05-05T00:45:48Z, see `JobStatusResponseBuilder`
_NOW = "2024-05-05T01:00:00+00:00"

_CONFIG: Dict[str, Any] = {
    "start_date": "2024-01-01",
    "shop": _SHOP_NAME,
    "credentials": {"auth_method": "api_password", "api_password": "api_password"},
}


def _order_line(
    order_id: int, order_created_at: str, order_updated_at: str, transaction_id: int, transaction_created_at: str, status: str
) -> str:
    transaction = {
        "id": f"gid://shopify/OrderTransaction/{transaction_id}",
        "errorCode": None,
        "test": False,
        "kind": "REFUND",
        "amount": "57.23",
        "createdAt": transaction_created_at,
        "status": status,
        "processedAt": transaction_created_at,
        "gateway": "shopify_payments",
        "paymentId": f"r{transaction_id}",
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
        "amountSet": {"shop_money": {"amount": "57.23", "currency": "EUR"}},
        "fees": [],
        "paymentDetails": {},
    }
    return json.dumps(
        {
            "__typename": "Order",
            "id": f"gid://shopify/Order/{order_id}",
            "currency": "EUR",
            "order_created_at": order_created_at,
            "order_updated_at": order_updated_at,
            "transactions": [transaction],
        }
    )


def _job_creation_request(start: str, end: str) -> HttpRequest:
    query = Transaction(_CONFIG).get("updated_at", start, end)
    return HttpRequest(url=_URL_GRAPHQL, body=json.dumps({"query": ShopifyBulkTemplates.prepare(query)}))


@freeze_time(_NOW)
def test_incremental_read_emits_status_change_of_transaction_older_than_state() -> None:
    """
    Shopify transactions have no `updatedAt`, so a refund moving from PENDING to SUCCESS keeps its `createdAt`
    and is only visible through its order's `updatedAt`. The BULK job already selects orders updated since the
    saved state, so their transactions must be emitted even when they were created before the state.
    """
    with HttpMocker() as http_mocker:
        set_up_shop(http_mocker, _SHOP_NAME)
        grant_all_scopes(http_mocker, _SHOP_NAME)
        http_mocker.post(
            _job_creation_request(_STATE_CREATED_AT, _NOW),
            JobCreationResponseBuilder().with_bulk_operation_id(_BULK_OPERATION_ID).build(),
        )
        http_mocker.post(
            create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
            JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
        )
        jsonl_lines: List[str] = [
            # order and refund were created before the state; the refund became SUCCESS afterwards -> emitted
            _order_line(1, "2024-05-03T09:00:00Z", "2024-05-05T00:10:00Z", 1001, "2024-05-04T18:00:00Z", "SUCCESS"),
            # order last updated before the state (e.g. selected by the lookback window) -> already synced, dropped
            _order_line(2, "2024-05-03T09:00:00Z", "2024-05-04T23:00:00Z", 1002, "2024-05-04T18:00:00Z", "SUCCESS"),
            # transaction created after the state -> emitted
            _order_line(3, "2024-05-05T00:20:00Z", "2024-05-05T00:21:00Z", 1003, "2024-05-05T00:20:00Z", "PENDING"),
        ]
        http_mocker.get(HttpRequest(_JOB_RESULT_URL), HttpResponse("\n".join(jsonl_lines) + "\n", status_code=200))

        state = StateBuilder().with_stream_state(_STREAM, {"created_at": _STATE_CREATED_AT}).build()
        catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
        output = read(SourceShopify(), _CONFIG, catalog, state=state)

        assert output.errors == []
        records = sorted((record.record.data for record in output.records), key=lambda record: record["id"])
        assert [(record["id"], record["status"]) for record in records] == [(1001, "SUCCESS"), (1003, "PENDING")]
        assert all("order_created_at" not in record and "order_updated_at" not in record for record in records)
        # re-emitting the older refund must not rewind the cursor
        assert output.most_recent_state.stream_state.__dict__ == {"created_at": "2024-05-05T00:20:00+00:00"}
