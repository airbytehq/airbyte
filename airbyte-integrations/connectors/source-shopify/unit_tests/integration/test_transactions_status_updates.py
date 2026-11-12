# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Shopify transactions have no `updatedAt`: a transaction whose `status` changes after it was created (e.g. a refund moving
from PENDING to SUCCESS) keeps its `created_at`. The only signal is its order's `updated_at`, which is what both variants
of the `transactions` stream use to select orders, so every transaction of a selected order has to be emitted.
"""

import json
from typing import Any, Dict, List, Optional

from freezegun import freeze_time
from source_shopify import SourceShopify
from source_shopify.shopify_graphql.bulk.query import ShopifyBulkTemplates, Transaction
from source_shopify.streams.base_streams import ShopifyStream
from source_shopify.utils import EagerlyCachedStreamState

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.integration.api.authentication import grant_all_scopes, set_up_shop
from unit_tests.integration.api.bulk import JobCreationResponseBuilder, JobStatusResponseBuilder, create_job_status_request


_SHOP_NAME = "airbyte-integration-test"
_STREAM = "transactions"
_BASE_URL = f"https://{_SHOP_NAME}.myshopify.com/admin/api/{ShopifyStream.api_version}"
_START_DATE = "2026-10-22"

_FIRST_SYNC_AT = "2026-10-22T15:01:00+00:00"
_SECOND_SYNC_AT = "2026-10-22T16:01:00+00:00"

# order 1: a sale and its refund, the refund is still PENDING during the first sync
_ORDER_ID = 1
_SALE_ID = 1001
_SALE_CREATED_AT = "2026-10-22T13:00:00+00:00"
_REFUND_ID = 1002
_REFUND_CREATED_AT = "2026-10-22T14:16:17+00:00"
# order 2: the most recent transaction of the shop, it defines the cursor saved by the first sync
_OTHER_ORDER_ID = 2
_OTHER_SALE_ID = 1003
_OTHER_SALE_CREATED_AT = "2026-10-22T14:59:10+00:00"
# order 1 is updated when its refund becomes SUCCESS, between the two syncs
_ORDER_UPDATED_AT_AFTER_REFUND_SUCCESS = "2026-10-22T15:12:00+00:00"

_EXPECTED_STATE_CURSOR = _OTHER_SALE_CREATED_AT


def _config(fetch_transactions_user_id: bool) -> Dict[str, Any]:
    return {
        "start_date": _START_DATE,
        "shop": _SHOP_NAME,
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "fetch_transactions_user_id": fetch_transactions_user_id,
    }


def _read(http_mocker: HttpMocker, config: Dict[str, Any], state: Optional[Dict[str, Any]] = None) -> EntrypointOutput:
    # every sync runs in its own process, the state cached by the previous one is not available
    EagerlyCachedStreamState.cached_state.clear()
    set_up_shop(http_mocker, _SHOP_NAME)
    grant_all_scopes(http_mocker, _SHOP_NAME)
    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
    airbyte_state = StateBuilder().with_stream_state(_STREAM, state).build() if state else None
    output = read(SourceShopify(), config, catalog, state=airbyte_state)
    assert output.errors == []
    return output


def _id_to_status(output: EntrypointOutput) -> Dict[int, str]:
    records = [message.record.data for message in output.records]
    id_to_status = {record["id"]: record["status"] for record in records}
    # no transaction is emitted twice within a single sync
    assert len(id_to_status) == len(records)
    return id_to_status


def _emitted_state(output: EntrypointOutput) -> Dict[str, Any]:
    return output.most_recent_state.stream_state.__dict__


# --------------------------- GraphQL BULK variant (default) ---------------------------


def _bulk_transaction(transaction_id: int, kind: str, status: str, created_at: str, parent_id: Optional[int] = None) -> Dict[str, Any]:
    return {
        "id": f"gid://shopify/OrderTransaction/{transaction_id}",
        "errorCode": None,
        "test": True,
        "kind": kind,
        "amount": "57.23",
        "createdAt": created_at.replace("+00:00", "Z"),
        "status": status,
        "processedAt": created_at.replace("+00:00", "Z"),
        "gateway": "bogus",
        "paymentId": f"c1.{transaction_id}",
        "accountNumber": "1",
        "formattedGateway": "bogus",
        "manuallyCapturable": False,
        "receipt": "{}",
        "parentTransaction": {"parentId": f"gid://shopify/OrderTransaction/{parent_id}"} if parent_id else None,
        "authorization": None,
        "totalUnsettledSet": {
            "presentmentMoney": {"amount": "0.0", "currency": "USD"},
            "shopMoney": {"amount": "0.0", "currency": "USD"},
        },
        "amountSet": {"shop_money": {"amount": "57.23", "currency": "USD"}},
        "fees": [],
        "paymentDetails": {},
    }


def _bulk_order(order_id: int, transactions: List[Dict[str, Any]]) -> str:
    return json.dumps({"__typename": "Order", "id": f"gid://shopify/Order/{order_id}", "currency": "USD", "transactions": transactions})


def _mock_bulk_job(http_mocker: HttpMocker, job_id: str, lower_boundary: str, upper_boundary: str, orders: List[str]) -> None:
    """
    The job creation request is matched on its exact body, so the test fails if the orders of the
    BULK job are not requested for the exact `updated_at` window `lower_boundary` -- `upper_boundary`.
    The list of the requested fields is not what this test is about, so it comes from the query builder.
    """
    query = Transaction({"shop": _SHOP_NAME}).get("updated_at", lower_boundary, upper_boundary)
    assert f"updated_at:>='{lower_boundary}' AND updated_at:<='{upper_boundary}'" in query
    job_number = job_id.split("/")[-1]
    result_url = (
        f"https://storage.googleapis.com/bulk-operation-outputs/{job_number}"
        f"?response-content-disposition=attachment%3B+filename%3D%22bulk-{job_number}.jsonl%22&response-content-type=application%2Fjsonl"
    )
    http_mocker.post(
        HttpRequest(url=f"{_BASE_URL}/graphql.json", body=json.dumps({"query": ShopifyBulkTemplates.prepare(query)})),
        JobCreationResponseBuilder(job_created_at=upper_boundary.replace("+00:00", "Z")).with_bulk_operation_id(job_id).build(),
    )
    http_mocker.post(
        create_job_status_request(_SHOP_NAME, job_id),
        JobStatusResponseBuilder().with_completed_status(job_id, result_url).build(),
    )
    http_mocker.get(HttpRequest(result_url), HttpResponse("\n".join(orders) + "\n", status_code=200))


def test_graphql_transactions_incremental_read_emits_status_change_of_existing_transaction() -> None:
    config = _config(fetch_transactions_user_id=False)
    sale = _bulk_transaction(_SALE_ID, "SALE", "SUCCESS", _SALE_CREATED_AT)
    other_order = _bulk_order(_OTHER_ORDER_ID, [_bulk_transaction(_OTHER_SALE_ID, "SALE", "SUCCESS", _OTHER_SALE_CREATED_AT)])

    with freeze_time(_FIRST_SYNC_AT), HttpMocker() as http_mocker:
        pending_refund = _bulk_transaction(_REFUND_ID, "REFUND", "PENDING", _REFUND_CREATED_AT, parent_id=_SALE_ID)
        _mock_bulk_job(
            http_mocker,
            "gid://shopify/BulkOperation/1",
            lower_boundary="2026-10-22T00:00:00+00:00",
            upper_boundary=_FIRST_SYNC_AT,
            orders=[_bulk_order(_ORDER_ID, [sale, pending_refund]), other_order],
        )
        first_sync = _read(http_mocker, config)

    assert _id_to_status(first_sync) == {_SALE_ID: "SUCCESS", _REFUND_ID: "PENDING", _OTHER_SALE_ID: "SUCCESS"}
    assert _emitted_state(first_sync) == {"created_at": _EXPECTED_STATE_CURSOR}

    with freeze_time(_SECOND_SYNC_AT), HttpMocker() as http_mocker:
        succeeded_refund = _bulk_transaction(_REFUND_ID, "REFUND", "SUCCESS", _REFUND_CREATED_AT, parent_id=_SALE_ID)
        # the orders updated since the saved cursor: order 2 sits on the inclusive lower boundary,
        # order 1 was updated by its refund status change
        _mock_bulk_job(
            http_mocker,
            "gid://shopify/BulkOperation/2",
            lower_boundary=_EXPECTED_STATE_CURSOR,
            upper_boundary=_SECOND_SYNC_AT,
            orders=[other_order, _bulk_order(_ORDER_ID, [sale, succeeded_refund])],
        )
        second_sync = _read(http_mocker, config, state=_emitted_state(first_sync))

    # the refund predates the saved cursor and is emitted again with its new status, together with the documented
    # overlap: the other transactions of the orders updated since the saved cursor
    assert _id_to_status(second_sync) == {_SALE_ID: "SUCCESS", _REFUND_ID: "SUCCESS", _OTHER_SALE_ID: "SUCCESS"}
    assert _emitted_state(second_sync) == {"created_at": _EXPECTED_STATE_CURSOR}


# --------------------------- REST variant (`fetch_transactions_user_id`) ---------------------------


def _rest_order(order_id: int, updated_at: str) -> Dict[str, Any]:
    return {"id": order_id, "created_at": _SALE_CREATED_AT, "updated_at": updated_at}


def _rest_transaction(transaction_id: int, order_id: int, kind: str, status: str, created_at: str) -> Dict[str, Any]:
    return {
        "id": transaction_id,
        "order_id": order_id,
        "kind": kind,
        "status": status,
        "amount": "57.23",
        "currency": "USD",
        "created_at": created_at,
        "processed_at": created_at,
        "user_id": 7,
    }


def _mock_rest_orders(http_mocker: HttpMocker, updated_at_min: str, deleted_at_min: Optional[str], orders: List[Dict[str, Any]]) -> None:
    http_mocker.get(
        HttpRequest(
            f"{_BASE_URL}/orders.json",
            query_params={"limit": "250", "order": "updated_at asc", "updated_at_min": updated_at_min, "status": "any"},
        ),
        HttpResponse(json.dumps({"orders": orders}), status_code=200),
    )
    deleted_events_params = {"filter": "Order", "verb": "destroy"}
    if deleted_at_min:
        deleted_events_params["created_at_min"] = deleted_at_min
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/events.json", query_params=deleted_events_params),
        HttpResponse(json.dumps({"events": []}), status_code=200),
    )


def _mock_rest_transactions(http_mocker: HttpMocker, order_id: int, transactions: List[Dict[str, Any]]) -> None:
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/orders/{order_id}/transactions.json", query_params={"limit": "250"}),
        HttpResponse(json.dumps({"transactions": transactions}), status_code=200),
    )


def test_rest_transactions_incremental_read_emits_status_change_of_existing_transaction() -> None:
    config = _config(fetch_transactions_user_id=True)
    sale = _rest_transaction(_SALE_ID, _ORDER_ID, "sale", "success", _SALE_CREATED_AT)
    other_sale = _rest_transaction(_OTHER_SALE_ID, _OTHER_ORDER_ID, "sale", "success", _OTHER_SALE_CREATED_AT)
    orders_updated_at_after_first_sync = _OTHER_SALE_CREATED_AT

    with freeze_time(_FIRST_SYNC_AT), HttpMocker() as http_mocker:
        _mock_rest_orders(
            http_mocker,
            updated_at_min=_START_DATE,
            deleted_at_min=None,
            orders=[_rest_order(_ORDER_ID, _REFUND_CREATED_AT), _rest_order(_OTHER_ORDER_ID, orders_updated_at_after_first_sync)],
        )
        pending_refund = _rest_transaction(_REFUND_ID, _ORDER_ID, "refund", "pending", _REFUND_CREATED_AT)
        _mock_rest_transactions(http_mocker, _ORDER_ID, [sale, pending_refund])
        _mock_rest_transactions(http_mocker, _OTHER_ORDER_ID, [other_sale])
        first_sync = _read(http_mocker, config)

    assert _id_to_status(first_sync) == {_SALE_ID: "success", _REFUND_ID: "pending", _OTHER_SALE_ID: "success"}
    first_sync_state = _emitted_state(first_sync)
    assert first_sync_state["created_at"] == _EXPECTED_STATE_CURSOR
    assert first_sync_state["orders"]["updated_at"] == orders_updated_at_after_first_sync

    with freeze_time(_SECOND_SYNC_AT), HttpMocker() as http_mocker:
        # the orders updated since the saved parent cursor: order 2 sits on the inclusive lower boundary,
        # order 1 was updated by its refund status change
        _mock_rest_orders(
            http_mocker,
            updated_at_min=orders_updated_at_after_first_sync,
            deleted_at_min=None,
            orders=[
                _rest_order(_OTHER_ORDER_ID, orders_updated_at_after_first_sync),
                _rest_order(_ORDER_ID, _ORDER_UPDATED_AT_AFTER_REFUND_SUCCESS),
            ],
        )
        succeeded_refund = _rest_transaction(_REFUND_ID, _ORDER_ID, "refund", "success", _REFUND_CREATED_AT)
        _mock_rest_transactions(http_mocker, _ORDER_ID, [sale, succeeded_refund])
        _mock_rest_transactions(http_mocker, _OTHER_ORDER_ID, [other_sale])
        second_sync = _read(http_mocker, config, state=first_sync_state)

    # the refund predates the saved cursor and is emitted again with its new status, together with the documented
    # overlap: the other transactions of the orders updated since the saved parent cursor
    assert _id_to_status(second_sync) == {_SALE_ID: "success", _REFUND_ID: "success", _OTHER_SALE_ID: "success"}
    second_sync_state = _emitted_state(second_sync)
    assert second_sync_state["created_at"] == _EXPECTED_STATE_CURSOR
    assert second_sync_state["orders"]["updated_at"] == _ORDER_UPDATED_AT_AFTER_REFUND_SUCCESS
