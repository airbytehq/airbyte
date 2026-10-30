#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from source_shopify.streams.streams import Transactions, TransactionsGraphql
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache

from airbyte_cdk.models import SyncMode


STATE = {"created_at": "2026-09-11T05:49:43+00:00"}

# Offsite (Klarna / Mollie) payment: the transaction is created on the payment provider's
# site before Shopify creates the order, so `transaction.created_at` < `order.created_at`.
OFFSITE_ORDER_ID = 6001
OFFSITE_ORDER_CREATED_AT = "2026-09-11T06:27:00Z"
OFFSITE_TRANSACTION_ID = 7001
OFFSITE_TRANSACTION_CREATED_AT = "2026-09-11T05:07:00Z"

# An old order, created before the state, that got updated (and so re-appears in the slice)
OLD_ORDER_ID = 6002
OLD_ORDER_CREATED_AT = "2026-09-01T10:00:00Z"
OLD_TRANSACTION_ID = 7002
OLD_TRANSACTION_CREATED_AT = "2026-09-01T10:00:00Z"


def _bulk_transaction(transaction_id: int, created_at: str) -> dict:
    return {
        "id": f"gid://shopify/OrderTransaction/{transaction_id}",
        "errorCode": None,
        "test": False,
        "kind": "SALE",
        "amount": "10.0",
        "createdAt": created_at,
        "status": "SUCCESS",
        "processedAt": created_at,
        "gateway": "klarna",
        "paymentId": f"p{transaction_id}",
        "accountNumber": None,
        "formattedGateway": "Klarna",
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
        "paymentDetails": None,
    }


def _bulk_order_line(order_id: int, order_created_at: str, transaction_id: int, transaction_created_at: str) -> str:
    return json.dumps(
        {
            "__typename": "Order",
            "id": f"gid://shopify/Order/{order_id}",
            "createdAt": order_created_at,
            "currency": "EUR",
            "transactions": [_bulk_transaction(transaction_id, transaction_created_at)],
        }
    )


@pytest.fixture(autouse=True)
def _reset_cached_state():
    stream_state_cache.cached_state.clear()
    yield
    stream_state_cache.cached_state.clear()


def _read_bulk_transactions(requests_mock, bulk_job_completed_response, auth_config, jsonl: str):
    stream = TransactionsGraphql(auth_config)
    test_result_url = bulk_job_completed_response.get("data").get("node").get("url")
    requests_mock.post(stream.job_manager.base_url, json=bulk_job_completed_response)
    requests_mock.get(test_result_url, text=jsonl)
    stream_state_cache.cached_state[stream.name] = dict(STATE)
    return list(stream.read_records(SyncMode.incremental, stream_slice={}, stream_state=dict(STATE)))


def test_bulk_transactions_query_requests_order_created_at(auth_config) -> None:
    stream = TransactionsGraphql(auth_config)
    query = stream.job_manager.query.get(filter_field="updated_at", start="2026-09-11T00:00:00+00:00", end="2026-09-12T00:00:00+00:00")
    order_node = query.split("transactions")[0]
    assert "createdAt" in order_node


def test_bulk_transactions_emit_offsite_transaction_created_before_state(requests_mock, bulk_job_completed_response, auth_config) -> None:
    jsonl = (
        _bulk_order_line(OFFSITE_ORDER_ID, OFFSITE_ORDER_CREATED_AT, OFFSITE_TRANSACTION_ID, OFFSITE_TRANSACTION_CREATED_AT)
        + "\n"
        + _bulk_order_line(OLD_ORDER_ID, OLD_ORDER_CREATED_AT, OLD_TRANSACTION_ID, OLD_TRANSACTION_CREATED_AT)
        + "\n"
    )
    records = _read_bulk_transactions(requests_mock, bulk_job_completed_response, auth_config, jsonl)

    # the offsite transaction of the new order is emitted, the already-synced transaction of the old order is not
    assert [record["id"] for record in records] == [OFFSITE_TRANSACTION_ID]
    assert records[0]["order_id"] == OFFSITE_ORDER_ID
    assert records[0]["created_at"] == "2026-09-11T05:07:00+00:00"
    # the helper field used for the state comparison is not part of the emitted record
    assert "order_created_at" not in records[0]


def test_rest_transactions_emit_offsite_transaction_created_before_state(requests_mock, auth_config) -> None:
    stream = Transactions(auth_config)
    orders_url = f"https://{auth_config['shop']}.myshopify.com/admin/api/{stream.api_version}/orders.json"
    requests_mock.get(
        orders_url,
        json={
            "orders": [
                {"id": OFFSITE_ORDER_ID, "created_at": "2026-09-11T06:27:00+00:00", "updated_at": "2026-09-11T06:27:05+00:00"},
                {"id": OLD_ORDER_ID, "created_at": "2026-09-01T10:00:00+00:00", "updated_at": "2026-09-11T06:30:00+00:00"},
            ]
        },
    )
    requests_mock.get(
        f"https://{auth_config['shop']}.myshopify.com/admin/api/{stream.api_version}/events.json",
        json={"events": []},
    )
    for order_id, transaction_id, created_at in (
        (OFFSITE_ORDER_ID, OFFSITE_TRANSACTION_ID, "2026-09-11T05:07:00+00:00"),
        (OLD_ORDER_ID, OLD_TRANSACTION_ID, "2026-09-01T10:00:00+00:00"),
    ):
        requests_mock.get(
            f"https://{auth_config['shop']}.myshopify.com/admin/api/{stream.api_version}/orders/{order_id}/transactions.json",
            json={"transactions": [{"id": transaction_id, "order_id": order_id, "created_at": created_at, "amount": "10.0"}]},
        )

    state = {**STATE, "orders": {"updated_at": "2026-09-11T05:49:43+00:00"}}
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.incremental, stream_state=state):
        records.extend(stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice, stream_state=state))

    assert [record["id"] for record in records] == [OFFSITE_TRANSACTION_ID]
    assert "order_created_at" not in records[0]
