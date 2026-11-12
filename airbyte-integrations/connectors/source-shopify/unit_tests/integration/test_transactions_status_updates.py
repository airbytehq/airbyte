# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json
from typing import Any, Dict, List

import pytest
from freezegun import freeze_time
from source_shopify import SourceShopify
from source_shopify.scopes import SCOPES_MAPPING
from source_shopify.streams.base_streams import ShopifyStream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


_SHOP_NAME = "airbyte-integration-test"
_API_URL = f"https://{_SHOP_NAME}.myshopify.com/admin/api/{ShopifyStream.api_version}"
_GRAPHQL_URL = f"{_API_URL}/graphql.json"
_JOB_ID = "gid://shopify/BulkOperation/4472588009661"
_JOB_RESULT_URL = (
    "https://storage.googleapis.com/bulk-operation-outputs/final"
    "?response-content-disposition=attachment;+filename=%22bulk-4476008693949.jsonl%22"
    ";+filename*=UTF-8%27%27bulk-4476008693949.jsonl&response-content-type=application/jsonl"
)

_NOW = "2026-10-22T16:01:00+00:00"
# the saved cursor is the `created_at` of the newest transaction emitted by the previous sync
_STATE_CREATED_AT = "2026-10-22T14:59:10+00:00"
# the refund was created (PENDING) before the saved cursor and became SUCCESS afterwards, which updated its order
_REFUND_ID = 9001
_REFUND_CREATED_AT = "2026-10-22T12:30:00Z"
_REFUND_ORDER_ID = 1
# a transaction created after the saved cursor
_NEW_SALE_ID = 9002
_NEW_SALE_CREATED_AT = "2026-10-22T15:10:00Z"
_NEW_SALE_ORDER_ID = 2


def _config(**overrides: Any) -> Dict[str, Any]:
    return {
        "start_date": "2026-10-01",
        "shop": _SHOP_NAME,
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "bulk_window_in_days": 1,
        **overrides,
    }


def _mock_shop_access(requests_mock) -> None:
    requests_mock.get(f"{_API_URL}/shop.json", json={"shop": {"id": 1}})
    all_scopes = [{"handle": scope} for stream_scopes in SCOPES_MAPPING.values() for scope in stream_scopes]
    requests_mock.get(f"https://{_SHOP_NAME}.myshopify.com/admin/oauth/access_scopes.json", json={"access_scopes": all_scopes})


def _read_transactions(config: Dict[str, Any], state: Dict[str, Any]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("transactions", SyncMode.incremental).build()
    return read(SourceShopify(), config, catalog, state=StateBuilder().with_stream_state("transactions", state).build())


def _emitted(output: EntrypointOutput) -> List[tuple]:
    return [(record.record.data["id"], record.record.data["status"]) for record in output.records]


def _bulk_order_line(order_id: int, transaction_id: int, kind: str, created_at: str) -> str:
    return json.dumps(
        {
            "__typename": "Order",
            "id": f"gid://shopify/Order/{order_id}",
            "currency": "EUR",
            "transactions": [
                {
                    "id": f"gid://shopify/OrderTransaction/{transaction_id}",
                    "errorCode": None,
                    "test": False,
                    "kind": kind,
                    "amount": "57.23",
                    "createdAt": created_at,
                    "status": "SUCCESS",
                    "processedAt": created_at,
                    "gateway": "shopify_payments",
                    "paymentId": "c25048437719229.1",
                    "accountNumber": "1",
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
            ],
        }
    )


@freeze_time(_NOW)
def test_bulk_transactions_incremental_read_emits_status_update_of_transaction_older_than_state(requests_mock) -> None:
    _mock_shop_access(requests_mock)
    job_creation = requests_mock.post(
        _GRAPHQL_URL,
        additional_matcher=lambda request: "bulkOperationRunQuery" in request.text,
        json={
            "data": {
                "bulkOperationRunQuery": {
                    "bulkOperation": {"id": _JOB_ID, "status": "CREATED", "createdAt": "2026-10-22T16:00:00Z"},
                    "userErrors": [],
                }
            }
        },
    )
    requests_mock.post(
        _GRAPHQL_URL,
        additional_matcher=lambda request: "bulkOperationRunQuery" not in request.text,
        json={
            "data": {
                "node": {
                    "id": _JOB_ID,
                    "status": "COMPLETED",
                    "errorCode": None,
                    "createdAt": "2026-10-22T16:00:00Z",
                    "objectCount": "2",
                    "fileSize": "774",
                    "url": _JOB_RESULT_URL,
                    "partialDataUrl": None,
                }
            }
        },
    )
    # Shopify returns both orders because both were updated after the saved cursor
    requests_mock.get(
        _JOB_RESULT_URL,
        text="\n".join(
            [
                _bulk_order_line(_REFUND_ORDER_ID, _REFUND_ID, "REFUND", _REFUND_CREATED_AT),
                _bulk_order_line(_NEW_SALE_ORDER_ID, _NEW_SALE_ID, "SALE", _NEW_SALE_CREATED_AT),
            ]
        )
        + "\n",
    )

    output = _read_transactions(_config(), {"created_at": _STATE_CREATED_AT})

    assert output.errors == []
    # orders are requested by `updated_at` from the saved cursor up to now, in a single job
    assert job_creation.call_count == 1
    assert f"updated_at:>='{_STATE_CREATED_AT}' AND updated_at:<='{_NOW}'" in job_creation.last_request.json()["query"]
    assert _emitted(output) == [(_REFUND_ID, "SUCCESS"), (_NEW_SALE_ID, "SUCCESS")]
    # re-emitting the older transaction does not move the cursor backwards
    assert output.most_recent_state.stream_state.created_at == "2026-10-22T15:10:00+00:00"


def _rest_transaction(transaction_id: int, order_id: int, kind: str, created_at: str) -> Dict[str, Any]:
    return {
        "id": transaction_id,
        "order_id": order_id,
        "kind": kind,
        "status": "success",
        "amount": "57.23",
        "currency": "EUR",
        "created_at": created_at,
        "processed_at": created_at,
        "user_id": 7,
    }


def test_rest_transactions_incremental_read_emits_status_update_of_transaction_older_than_state(requests_mock) -> None:
    orders_updated_at_state = "2026-10-22T14:59:00+00:00"
    _mock_shop_access(requests_mock)
    # Shopify returns both orders because both were updated after the saved parent cursor
    orders = requests_mock.get(
        f"{_API_URL}/orders.json",
        json={
            "orders": [
                {"id": _REFUND_ORDER_ID, "updated_at": "2026-10-22T15:05:00+00:00"},
                {"id": _NEW_SALE_ORDER_ID, "updated_at": "2026-10-22T15:10:00+00:00"},
            ]
        },
    )
    requests_mock.get(f"{_API_URL}/events.json", json={"events": []})
    requests_mock.get(
        f"{_API_URL}/orders/{_REFUND_ORDER_ID}/transactions.json",
        json={"transactions": [_rest_transaction(_REFUND_ID, _REFUND_ORDER_ID, "refund", "2026-10-22T12:30:00+00:00")]},
    )
    requests_mock.get(
        f"{_API_URL}/orders/{_NEW_SALE_ORDER_ID}/transactions.json",
        json={"transactions": [_rest_transaction(_NEW_SALE_ID, _NEW_SALE_ORDER_ID, "sale", "2026-10-22T15:10:00+00:00")]},
    )

    output = _read_transactions(
        _config(fetch_transactions_user_id=True),
        {"created_at": _STATE_CREATED_AT, "orders": {"updated_at": orders_updated_at_state, "deleted": {"deleted_at": ""}}},
    )

    assert output.errors == []
    # parent orders are requested from the saved parent cursor
    # `requests_mock` lowercases the parsed query string
    assert orders.request_history[0].qs["updated_at_min"] == [orders_updated_at_state.lower()]
    assert _emitted(output) == [(_REFUND_ID, "success"), (_NEW_SALE_ID, "success")]
    final_state = output.most_recent_state.stream_state
    # re-emitting the older transaction does not move the cursor backwards
    assert final_state.created_at == "2026-10-22T15:10:00+00:00"
    assert final_state.orders["updated_at"] == "2026-10-22T15:10:00+00:00"
