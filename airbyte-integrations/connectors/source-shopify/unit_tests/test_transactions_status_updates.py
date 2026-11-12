#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime
from typing import Any, Dict, List, Mapping

import pytest
from freezegun import freeze_time
from source_shopify import SourceShopify
from source_shopify.scopes import SCOPES_MAPPING
from source_shopify.streams.base_streams import ShopifyStream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


_SHOP = "test-shop"
_API_URL = f"https://{_SHOP}.myshopify.com/admin/api/{ShopifyStream.api_version}"
_NOW = datetime.fromisoformat("2026-10-22T16:01:00+00:00")

# the cursor saved by the previous sync, every transaction below except the newest one was created before it
_STATE_CREATED_AT = "2026-10-22T14:59:10+00:00"
_PARENT_STATE_UPDATED_AT = "2026-10-22T15:00:00+00:00"

_ORDER_ID = 1
_REFUND_ID = 1001
_REFUND_CREATED_AT = "2026-10-22T13:00:00+00:00"
_NEW_SALE_ID = 2002
_NEW_SALE_CREATED_AT = "2026-10-22T15:30:00+00:00"
# the order was updated after the previous sync, when its pending refund settled
_ORDER_UPDATED_AT = "2026-10-22T15:10:00+00:00"
_NEW_ORDER_ID = 2
_NEW_ORDER_UPDATED_AT = "2026-10-22T15:30:00+00:00"


def _config(fetch_transactions_user_id: bool) -> Dict[str, Any]:
    return {
        "shop": _SHOP,
        "start_date": "2026-10-01",
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "fetch_transactions_user_id": fetch_transactions_user_id,
    }


def _mock_shop(requests_mock) -> None:
    requests_mock.get(f"{_API_URL}/shop.json", json={"shop": {"id": 1}})
    all_scopes = [scope for stream_scopes in SCOPES_MAPPING.values() for scope in stream_scopes]
    requests_mock.get(
        f"https://{_SHOP}.myshopify.com/admin/oauth/access_scopes.json",
        json={"access_scopes": [{"handle": scope} for scope in all_scopes]},
    )


def _graphql_transaction(transaction_id: int, kind: str, status: str, created_at: str) -> Mapping[str, Any]:
    return {
        "id": f"gid://shopify/OrderTransaction/{transaction_id}",
        "errorCode": None,
        "test": False,
        "kind": kind,
        "amount": "57.23",
        "createdAt": created_at,
        "status": status,
        "processedAt": created_at,
        "gateway": "bogus",
        "paymentId": f"c{transaction_id}.1",
        "accountNumber": "1",
        "formattedGateway": "bogus",
        "manuallyCapturable": False,
        "receipt": "{}",
        "parentTransaction": None,
        "authorization": None,
        "totalUnsettledSet": {
            "presentmentMoney": {"amount": "0.0", "currency": "USD"},
            "shopMoney": {"amount": "0.0", "currency": "USD"},
        },
        "amountSet": {"shop_money": {"amount": "57.23", "currency": "USD"}},
        "fees": [],
        "paymentDetails": {},
    }


def _graphql_order(order_id: int, transactions: List[Mapping[str, Any]]) -> str:
    return json.dumps(
        {
            "__typename": "Order",
            "id": f"gid://shopify/Order/{order_id}",
            "currency": "USD",
            "transactions": transactions,
        }
    )


def _mock_graphql_bulk_api(requests_mock, bulk_job_completed_response) -> None:
    """
    Serves the orders Shopify returns for `updated_at:>=<state>`: the order whose refund settled and a new order.
    """
    result_url = bulk_job_completed_response["data"]["node"]["url"]
    requests_mock.post(f"{_API_URL}/graphql.json", json=bulk_job_completed_response)
    requests_mock.get(
        result_url,
        text="\n".join(
            [
                _graphql_order(_ORDER_ID, [_graphql_transaction(_REFUND_ID, "REFUND", "SUCCESS", "2026-10-22T13:00:00Z")]),
                _graphql_order(_NEW_ORDER_ID, [_graphql_transaction(_NEW_SALE_ID, "SALE", "SUCCESS", "2026-10-22T15:30:00Z")]),
            ]
        )
        + "\n",
    )


def _mock_rest_api(requests_mock) -> None:
    """
    Serves the orders Shopify returns for `updated_at_min=<parent state>`: the order whose refund settled and a new order.
    """
    requests_mock.get(
        f"{_API_URL}/orders.json",
        json={
            "orders": [
                {"id": _ORDER_ID, "updated_at": _ORDER_UPDATED_AT},
                {"id": _NEW_ORDER_ID, "updated_at": _NEW_ORDER_UPDATED_AT},
            ]
        },
    )
    requests_mock.get(f"{_API_URL}/events.json", json={"events": []})
    requests_mock.get(
        f"{_API_URL}/orders/{_ORDER_ID}/transactions.json",
        json={
            "transactions": [
                {"id": _REFUND_ID, "order_id": _ORDER_ID, "kind": "refund", "status": "success", "created_at": _REFUND_CREATED_AT}
            ]
        },
    )
    requests_mock.get(
        f"{_API_URL}/orders/{_NEW_ORDER_ID}/transactions.json",
        json={
            "transactions": [
                {"id": _NEW_SALE_ID, "order_id": _NEW_ORDER_ID, "kind": "sale", "status": "success", "created_at": _NEW_SALE_CREATED_AT}
            ]
        },
    )


def _read_transactions(config: Dict[str, Any], stream_state: Mapping[str, Any]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("transactions", SyncMode.incremental).build()
    state = StateBuilder().with_stream_state("transactions", stream_state).build()
    return read(SourceShopify(), config, catalog, state=state)


@freeze_time(_NOW)
@pytest.mark.parametrize(
    "fetch_transactions_user_id, stream_state, expected_state",
    [
        pytest.param(
            False,
            {"created_at": _STATE_CREATED_AT},
            {"created_at": _NEW_SALE_CREATED_AT},
            id="graphql_bulk_transactions",
        ),
        pytest.param(
            True,
            {"created_at": _STATE_CREATED_AT, "orders": {"updated_at": _PARENT_STATE_UPDATED_AT}},
            {
                "created_at": _NEW_SALE_CREATED_AT,
                "orders": {"updated_at": _NEW_ORDER_UPDATED_AT, "deleted": {"deleted_at": ""}},
            },
            id="rest_transactions_with_user_id",
        ),
    ],
)
def test_incremental_read_emits_status_change_of_transaction_created_before_state(
    requests_mock,
    bulk_job_completed_response,
    fetch_transactions_user_id,
    stream_state,
    expected_state,
) -> None:
    """
    A refund transaction is created as PENDING and settles to SUCCESS later, which updates its order but not the
    transaction's `created_at`. The incremental sync that picks up the updated order must emit the transaction again,
    even though its `created_at` is older than the saved cursor, and must never move the cursor backwards.
    """
    _mock_shop(requests_mock)
    _mock_graphql_bulk_api(requests_mock, bulk_job_completed_response)
    _mock_rest_api(requests_mock)

    output = _read_transactions(_config(fetch_transactions_user_id), stream_state)

    assert output.errors == []
    assert [(record.record.data["id"], record.record.data["status"].lower()) for record in output.records] == [
        (_REFUND_ID, "success"),
        (_NEW_SALE_ID, "success"),
    ]
    assert output.most_recent_state.stream_state.__dict__ == expected_state
