# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json
from typing import Any, Dict, List, Optional

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
_JOB_RESULT_URL = "https://storage.googleapis.com/bulk-operation-outputs/final?response-content-disposition=attachment%3B+filename%3D%22bulk-123.jsonl%22%3B+filename%2A%3DUTF-8%27%27bulk-123.jsonl&response-content-type=application%2Fjsonl"

_STATE_CREATED_AT = "2026-10-22T14:59:10+00:00"
_NOW = "2026-10-22T16:00:00+00:00"


def _config() -> Dict[str, Any]:
    return {
        "start_date": "2026-01-01",
        "shop": _SHOP_NAME,
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "bulk_window_in_days": 30,
        "lookback_window_in_days": 1,
    }


def _order_line(
    order_id: int, created_at: str, updated_at: Optional[str], transaction_id: int, transaction_created_at: str, status: str
) -> str:
    order: Dict[str, Any] = {
        "__typename": "Order",
        "id": f"gid://shopify/Order/{order_id}",
        "currency": "EUR",
        "order_created_at": created_at,
        "transactions": [
            {
                "id": f"gid://shopify/OrderTransaction/{transaction_id}",
                "errorCode": None,
                "test": False,
                "kind": "REFUND",
                "amount": "10.0",
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
                "amountSet": {"shop_money": {"amount": "10.0", "currency": "EUR"}},
                "fees": [],
                "paymentDetails": {},
            }
        ],
    }
    if updated_at is not None:
        order["order_updated_at"] = updated_at
    return json.dumps(order)


def _read(http_mocker: HttpMocker, jsonl_lines: List[str]):
    # the bulk job covers orders updated since the saved state minus the 1 day lookback window
    job_query = Transaction(_config()).get("updated_at", "2026-10-21T14:59:10+00:00", _NOW)
    http_mocker.post(
        HttpRequest(_URL_GRAPHQL, body=json.dumps({"query": ShopifyBulkTemplates.prepare(job_query)})),
        JobCreationResponseBuilder(job_created_at="2026-10-22T15:55:00Z").with_bulk_operation_id(_BULK_OPERATION_ID).build(),
    )
    http_mocker.post(
        create_job_status_request(_SHOP_NAME, _BULK_OPERATION_ID),
        JobStatusResponseBuilder().with_completed_status(_BULK_OPERATION_ID, _JOB_RESULT_URL).build(),
    )
    http_mocker.get(HttpRequest(_JOB_RESULT_URL), HttpResponse("\n".join(jsonl_lines) + "\n", status_code=200))

    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
    state = StateBuilder().with_stream_state(_STREAM, {"created_at": _STATE_CREATED_AT}).build()
    return read(SourceShopify(), _config(), catalog, state=state)


@freeze_time(_NOW)
def test_incremental_read_emits_status_change_of_transaction_created_before_state() -> None:
    with HttpMocker() as http_mocker:
        set_up_shop(http_mocker, _SHOP_NAME)
        grant_all_scopes(http_mocker, _SHOP_NAME)
        output = _read(
            http_mocker,
            [
                # refund and its order were created before the saved state; the refund turned SUCCESS afterwards,
                # which moved the order's `updatedAt` past the saved state -> the updated refund is emitted
                _order_line(1, "2026-10-22T10:00:00Z", "2026-10-22T15:05:00Z", 1001, "2026-10-22T12:00:00Z", "SUCCESS"),
                # order returned only because of the lookback window: nothing changed since the saved state -> not emitted
                _order_line(2, "2026-10-22T09:00:00Z", "2026-10-22T14:00:00Z", 1002, "2026-10-22T09:30:00Z", "SUCCESS"),
                # transaction created after the saved state -> emitted
                _order_line(3, "2026-10-22T15:10:00Z", "2026-10-22T15:20:00Z", 1003, "2026-10-22T15:20:00Z", "PENDING"),
            ],
        )

    assert output.errors == []
    records = [message.record.data for message in output.records]
    assert [(record["id"], record["status"]) for record in records] == [(1001, "SUCCESS"), (1003, "PENDING")]
    assert all("order_created_at" not in record and "order_updated_at" not in record for record in records)
    # emitting the older transaction must not move the `created_at` cursor backwards
    assert output.most_recent_state.stream_state.__dict__ == {"created_at": "2026-10-22T15:20:00+00:00"}
