# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime
from typing import Any, Dict, List, Mapping, Tuple

import pytest
from freezegun import freeze_time
from source_shopify import SourceShopify
from source_shopify.shopify_graphql.bulk.query import ShopifyBulkTemplates, Transaction
from source_shopify.streams.base_streams import ShopifyStream
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.integration.api.authentication import grant_all_scopes, set_up_shop
from unit_tests.integration.api.bulk import JobCreationResponseBuilder, JobStatusResponseBuilder, create_job_status_request


_SHOP_NAME = "airbyte-integration-test"
_STREAM = "transactions"
_URL_BASE = f"https://{_SHOP_NAME}.myshopify.com/admin/api/{ShopifyStream.api_version}"

# The refund is created as PENDING before the first sync and only becomes SUCCESS after that sync,
# once a newer transaction of another order has already moved the `created_at` cursor past it.
_REFUNDED_ORDER_ID = 1
_REFUND_ID = 5001
_REFUND_CREATED_AT = "2026-10-22T10:00:00+00:00"
_CURSOR_MOVING_ORDER_ID = 2
_CURSOR_MOVING_TRANSACTION_ID = 5002
_CURSOR_MOVING_TRANSACTION_CREATED_AT = "2026-10-22T14:59:10+00:00"
_NEW_ORDER_ID = 3
_NEW_TRANSACTION_ID = 5003
_NEW_TRANSACTION_CREATED_AT = "2026-10-22T15:30:00+00:00"

_INITIAL_CURSOR = "2026-10-22T08:00:00+00:00"
_FIRST_SYNC_TIME = "2026-10-22T15:01:00+00:00"
_SECOND_SYNC_TIME = "2026-10-22T16:01:00+00:00"

# (order id, transaction id, transaction created_at, transaction status) served to each sync
_FIRST_SYNC_TRANSACTIONS = [
    (_REFUNDED_ORDER_ID, _REFUND_ID, _REFUND_CREATED_AT, "PENDING"),
    (_CURSOR_MOVING_ORDER_ID, _CURSOR_MOVING_TRANSACTION_ID, _CURSOR_MOVING_TRANSACTION_CREATED_AT, "SUCCESS"),
]
_SECOND_SYNC_TRANSACTIONS = [
    (_REFUNDED_ORDER_ID, _REFUND_ID, _REFUND_CREATED_AT, "SUCCESS"),
    (_NEW_ORDER_ID, _NEW_TRANSACTION_ID, _NEW_TRANSACTION_CREATED_AT, "SUCCESS"),
]

_Transaction = Tuple[int, int, str, str]


def _config(fetch_transactions_user_id: bool) -> Dict[str, Any]:
    return {
        "start_date": "2026-10-01",
        "shop": _SHOP_NAME,
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "bulk_window_in_days": 1,
        "fetch_transactions_user_id": fetch_transactions_user_id,
    }


def _mock_bulk_sync(http_mocker: HttpMocker, sync_index: int, lower_boundary: str, upper_boundary: str, transactions: List[_Transaction]):
    """GraphQL BULK `transactions`: one job over the orders updated within the slice."""
    bulk_operation_id = f"gid://shopify/BulkOperation/{sync_index}"
    job_result_url = (
        f"https://storage.googleapis.com/bulk-operation-outputs/bulk-{sync_index}"
        f"?response-content-disposition=attachment%3B+filename%3D%22bulk-{sync_index}.jsonl%22"
    )
    # the BULK query is built by the connector's own query builder, since the query shape is not what this test pins;
    # the slice boundaries (the orders `updated_at` filter) are still matched exactly
    query = Transaction(_config(False)).get("updated_at", lower_boundary, upper_boundary)
    http_mocker.post(
        HttpRequest(url=f"{_URL_BASE}/graphql.json", body=json.dumps({"query": ShopifyBulkTemplates.prepare(query)})),
        JobCreationResponseBuilder(job_created_at=upper_boundary).with_bulk_operation_id(bulk_operation_id).build(),
    )
    http_mocker.post(
        create_job_status_request(_SHOP_NAME, bulk_operation_id),
        JobStatusResponseBuilder().with_completed_status(bulk_operation_id, job_result_url).build(),
    )
    lines = [
        json.dumps(
            {
                "__typename": "Order",
                "id": f"gid://shopify/Order/{order_id}",
                "currency": "USD",
                "order_created_at": "2026-10-22T07:00:00Z",
                "transactions": [
                    {
                        "id": f"gid://shopify/OrderTransaction/{transaction_id}",
                        "kind": "REFUND",
                        "amount": "57.23",
                        "createdAt": created_at.replace("+00:00", "Z"),
                        "status": status,
                        "processedAt": created_at.replace("+00:00", "Z"),
                        "gateway": "bogus",
                        "receipt": "{}",
                        "parentTransaction": None,
                        "fees": [],
                        "paymentDetails": {},
                    }
                ],
            }
        )
        for order_id, transaction_id, created_at, status in transactions
    ]
    http_mocker.get(HttpRequest(job_result_url), HttpResponse("\n".join(lines) + "\n", status_code=200))


def _mock_rest_sync(http_mocker: HttpMocker, sync_index: int, lower_boundary: str, upper_boundary: str, transactions: List[_Transaction]):
    """REST `transactions` (`fetch_transactions_user_id`): one request per order updated since the parent `orders` state."""
    orders = [{"id": order_id, "updated_at": upper_boundary} for order_id, *_ in transactions]
    http_mocker.get(
        HttpRequest(
            f"{_URL_BASE}/orders.json",
            query_params={"limit": "250", "order": "updated_at asc", "updated_at_min": lower_boundary, "status": "any"},
        ),
        HttpResponse(json.dumps({"orders": orders}), status_code=200),
    )
    http_mocker.get(
        HttpRequest(f"{_URL_BASE}/events.json", query_params={"filter": "Order", "verb": "destroy"}),
        HttpResponse(json.dumps({"events": []}), status_code=200),
    )
    for order_id, transaction_id, created_at, status in transactions:
        http_mocker.get(
            HttpRequest(f"{_URL_BASE}/orders/{order_id}/transactions.json", query_params={"limit": "250"}),
            HttpResponse(
                json.dumps(
                    {
                        "transactions": [
                            {"id": transaction_id, "order_id": order_id, "kind": "refund", "status": status, "created_at": created_at}
                        ]
                    }
                ),
                status_code=200,
            ),
        )


def _read(fetch_transactions_user_id: bool, state: Mapping[str, Any]) -> EntrypointOutput:
    # every sync runs in its own process, so the process-wide state cache always starts empty
    stream_state_cache.cached_state.clear()
    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
    return read(SourceShopify(), _config(fetch_transactions_user_id), catalog, StateBuilder().with_stream_state(_STREAM, state).build())


def _state(output: EntrypointOutput) -> Dict[str, Any]:
    return dict(output.most_recent_state.stream_state.__dict__)


def _emitted(output: EntrypointOutput) -> List[Tuple[int, str]]:
    return sorted((record.record.data["id"], record.record.data["status"].upper()) for record in output.records)


@pytest.mark.parametrize(
    "fetch_transactions_user_id, mock_sync, initial_state, first_sync_lower_boundary, second_sync_lower_boundary",
    [
        pytest.param(
            False,
            _mock_bulk_sync,
            {"created_at": _INITIAL_CURSOR},
            _INITIAL_CURSOR,
            # the BULK stream filters the orders by `updated_at` starting from its own `created_at` cursor
            _CURSOR_MOVING_TRANSACTION_CREATED_AT,
            id="graphql_bulk",
        ),
        pytest.param(
            True,
            _mock_rest_sync,
            {"created_at": _INITIAL_CURSOR, "orders": {"updated_at": _INITIAL_CURSOR}},
            _INITIAL_CURSOR,
            # the REST stream filters the orders by `updated_at` starting from the parent `orders` state
            _FIRST_SYNC_TIME,
            id="rest_with_user_id",
        ),
    ],
)
def test_transaction_status_change_is_emitted_after_cursor_moved_past_its_created_at(
    fetch_transactions_user_id, mock_sync, initial_state, first_sync_lower_boundary, second_sync_lower_boundary
) -> None:
    with freeze_time(datetime.fromisoformat(_FIRST_SYNC_TIME)), HttpMocker() as http_mocker:
        set_up_shop(http_mocker, _SHOP_NAME)
        grant_all_scopes(http_mocker, _SHOP_NAME)
        mock_sync(http_mocker, 1, first_sync_lower_boundary, _FIRST_SYNC_TIME, _FIRST_SYNC_TRANSACTIONS)
        first_sync = _read(fetch_transactions_user_id, initial_state)
    first_sync_state = _state(first_sync)

    # the second sync starts from the state emitted by the first one
    with freeze_time(datetime.fromisoformat(_SECOND_SYNC_TIME)), HttpMocker() as http_mocker:
        set_up_shop(http_mocker, _SHOP_NAME)
        grant_all_scopes(http_mocker, _SHOP_NAME)
        mock_sync(http_mocker, 2, second_sync_lower_boundary, _SECOND_SYNC_TIME, _SECOND_SYNC_TRANSACTIONS)
        second_sync = _read(fetch_transactions_user_id, first_sync_state)

    assert first_sync.errors == []
    assert _emitted(first_sync) == [(_REFUND_ID, "PENDING"), (_CURSOR_MOVING_TRANSACTION_ID, "SUCCESS")]
    assert first_sync_state["created_at"] == _CURSOR_MOVING_TRANSACTION_CREATED_AT

    assert second_sync.errors == []
    # the refund predates the saved cursor, its order was updated since the previous sync -> the new status is emitted
    assert _emitted(second_sync) == [(_REFUND_ID, "SUCCESS"), (_NEW_TRANSACTION_ID, "SUCCESS")]
    assert _state(second_sync)["created_at"] == _NEW_TRANSACTION_CREATED_AT
