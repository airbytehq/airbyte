# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional

from freezegun import freeze_time
from source_shopify import SourceShopify
from source_shopify.streams.base_streams import ShopifyStream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.integration.api.authentication import grant_all_scopes, set_up_shop
from unit_tests.integration.api.bulk import (
    JobCreationResponseBuilder,
    JobStatusResponseBuilder,
    create_job_status_request,
)


_SHOP_NAME = "airbyte-integration-test"
_STREAM = "transactions"
_BASE_URL = f"https://{_SHOP_NAME}.myshopify.com/admin/api/{ShopifyStream.api_version}"
_JOB_RESULT_URL = "https://storage.googleapis.com/shopify-tiers-assets-prod-us-east1/bulk-operation-outputs/transactions.jsonl"

_NOW = "2026-10-22T16:01:00+00:00"
# the cursor saved by the previous sync
_STATE_CREATED_AT = "2026-10-22T14:59:10+00:00"

# the refund was created (and synced as PENDING) before the saved cursor, then settled, which only updates its order
_REFUND_ORDER_ID = 1
_REFUND_ID = 1001
_REFUND_CREATED_AT = "2026-10-21T09:00:00+00:00"
# a regular sale created after the saved cursor
_SALE_ORDER_ID = 2
_SALE_ID = 1002
_SALE_CREATED_AT = "2026-10-22T15:30:00+00:00"


def _config(fetch_transactions_user_id: bool) -> Dict[str, Any]:
    return {
        "start_date": "2026-01-01",
        "shop": _SHOP_NAME,
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
        "fetch_transactions_user_id": fetch_transactions_user_id,
    }


def _read(config: Mapping[str, Any], state: Mapping[str, Any]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
    return read(SourceShopify(), config, catalog, state=StateBuilder().with_stream_state(_STREAM, state).build())


def _emitted(output: EntrypointOutput) -> List[tuple]:
    return [(record.record.data["id"], record.record.data["status"]) for record in output.records]


def _bulk_order(order_id: int, transaction_id: int, kind: str, status: str, created_at: str) -> str:
    return json.dumps(
        {
            "__typename": "Order",
            "id": f"gid://shopify/Order/{order_id}",
            "currency": "USD",
            "transactions": [
                {
                    "id": f"gid://shopify/OrderTransaction/{transaction_id}",
                    "errorCode": None,
                    "test": False,
                    "kind": kind,
                    "amount": "57.23",
                    "createdAt": created_at.replace("+00:00", "Z"),
                    "status": status,
                    "processedAt": created_at.replace("+00:00", "Z"),
                    "gateway": "shopify_payments",
                    "parentTransaction": None,
                    "fees": [],
                    "paymentDetails": {},
                }
            ],
        }
    )


def _mock_bulk_job(http_mocker: HttpMocker, job_id: str, lower_boundary: str, result_lines: Optional[List[str]]) -> None:
    """Serves a completed BULK job, only for the job requesting the orders updated since `lower_boundary`."""
    orders_filter = f"updated_at:>='{lower_boundary}' AND updated_at:<='{_NOW}'"
    http_mocker.__getattribute__("_mocker").register_uri(
        "POST",
        f"{_BASE_URL}/graphql.json",
        text=JobCreationResponseBuilder(job_created_at="2026-10-22T16:00:00Z").with_bulk_operation_id(job_id).build().body,
        additional_matcher=lambda request: "bulkOperationRunQuery" in request.text and orders_filter in request.text,
    )
    filename = f"bulk-{job_id.rsplit('/', 1)[-1]}.jsonl"
    content_disposition = f"attachment%3B+filename%3D%22{filename}%22%3B+filename%2A%3DUTF-8%27%27{filename}"
    result_url = f"{_JOB_RESULT_URL}?response-content-disposition={content_disposition}"
    http_mocker.post(
        create_job_status_request(_SHOP_NAME, job_id),
        JobStatusResponseBuilder().with_completed_status(job_id, result_url if result_lines else None).build(),
    )
    if result_lines:
        http_mocker.get(HttpRequest(result_url), HttpResponse("\n".join(result_lines) + "\n", status_code=200))


@freeze_time(datetime.fromisoformat(_NOW))
def test_bulk_transactions_incremental_read_emits_status_change_of_transaction_created_before_state() -> None:
    config = _config(fetch_transactions_user_id=False)

    with HttpMocker() as http_mocker:
        set_up_shop(http_mocker, _SHOP_NAME)
        grant_all_scopes(http_mocker, _SHOP_NAME)
        _mock_bulk_job(
            http_mocker,
            "gid://shopify/BulkOperation/1",
            lower_boundary=_STATE_CREATED_AT,
            result_lines=[
                _bulk_order(_REFUND_ORDER_ID, _REFUND_ID, "REFUND", "SUCCESS", _REFUND_CREATED_AT),
                _bulk_order(_SALE_ORDER_ID, _SALE_ID, "SALE", "SUCCESS", _SALE_CREATED_AT),
            ],
        )
        output = _read(config, {"created_at": _STATE_CREATED_AT})

    assert output.errors == []
    assert _emitted(output) == [(_REFUND_ID, "SUCCESS"), (_SALE_ID, "SUCCESS")]
    # the refund predating the saved cursor does not move the cursor backwards
    assert output.most_recent_state.stream_state.created_at == _SALE_CREATED_AT

    # the next sync only asks for the orders updated since the emitted cursor, the settled refund is not requested again
    with HttpMocker() as http_mocker:
        set_up_shop(http_mocker, _SHOP_NAME)
        grant_all_scopes(http_mocker, _SHOP_NAME)
        _mock_bulk_job(http_mocker, "gid://shopify/BulkOperation/2", lower_boundary=_SALE_CREATED_AT, result_lines=None)
        next_output = _read(config, {"created_at": output.most_recent_state.stream_state.created_at})

    assert next_output.errors == []
    assert _emitted(next_output) == []


def _rest_order(order_id: int, updated_at: str) -> Dict[str, Any]:
    return {"id": order_id, "created_at": "2026-10-20T08:00:00+00:00", "updated_at": updated_at}


def _rest_transaction(order_id: int, transaction_id: int, kind: str, status: str, created_at: str) -> Dict[str, Any]:
    return {"id": transaction_id, "order_id": order_id, "kind": kind, "status": status, "created_at": created_at, "user_id": 7}


def _mock_rest_orders(http_mocker: HttpMocker, updated_at_min: str, orders: List[Dict[str, Any]]) -> None:
    http_mocker.get(
        HttpRequest(
            f"{_BASE_URL}/orders.json",
            query_params={"limit": "250", "order": "updated_at asc", "updated_at_min": updated_at_min, "status": "any"},
        ),
        HttpResponse(json.dumps({"orders": orders}), status_code=200),
    )
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/events.json", query_params={"filter": "Order", "verb": "destroy"}),
        HttpResponse(json.dumps({"events": []}), status_code=200),
    )


def _mock_rest_transactions(http_mocker: HttpMocker, order_id: int, transactions: List[Dict[str, Any]]) -> None:
    http_mocker.get(
        HttpRequest(f"{_BASE_URL}/orders/{order_id}/transactions.json", query_params={"limit": "250"}),
        HttpResponse(json.dumps({"transactions": transactions}), status_code=200),
    )


@freeze_time(datetime.fromisoformat(_NOW))
def test_rest_transactions_incremental_read_emits_status_change_of_transaction_created_before_state() -> None:
    config = _config(fetch_transactions_user_id=True)
    refund_order_updated_at = "2026-10-22T15:10:00+00:00"
    sale_order_updated_at = "2026-10-22T15:30:00+00:00"

    with HttpMocker() as http_mocker:
        set_up_shop(http_mocker, _SHOP_NAME)
        grant_all_scopes(http_mocker, _SHOP_NAME)
        _mock_rest_orders(
            http_mocker,
            updated_at_min=_STATE_CREATED_AT,
            orders=[_rest_order(_REFUND_ORDER_ID, refund_order_updated_at), _rest_order(_SALE_ORDER_ID, sale_order_updated_at)],
        )
        _mock_rest_transactions(
            http_mocker, _REFUND_ORDER_ID, [_rest_transaction(_REFUND_ORDER_ID, _REFUND_ID, "refund", "success", _REFUND_CREATED_AT)]
        )
        _mock_rest_transactions(
            http_mocker, _SALE_ORDER_ID, [_rest_transaction(_SALE_ORDER_ID, _SALE_ID, "sale", "success", _SALE_CREATED_AT)]
        )
        output = _read(config, {"created_at": _STATE_CREATED_AT, "orders": {"updated_at": _STATE_CREATED_AT}})

    assert output.errors == []
    assert _emitted(output) == [(_REFUND_ID, "success"), (_SALE_ID, "success")]
    state = output.most_recent_state.stream_state
    # the refund predating the saved cursor does not move the cursor backwards
    assert state.created_at == _SALE_CREATED_AT
    assert state.orders["updated_at"] == sale_order_updated_at

    # the next sync only asks for the orders updated since the emitted parent cursor (inclusive),
    # so the settled refund is not read again
    with HttpMocker() as http_mocker:
        set_up_shop(http_mocker, _SHOP_NAME)
        grant_all_scopes(http_mocker, _SHOP_NAME)
        _mock_rest_orders(http_mocker, updated_at_min=sale_order_updated_at, orders=[_rest_order(_SALE_ORDER_ID, sale_order_updated_at)])
        _mock_rest_transactions(
            http_mocker, _SALE_ORDER_ID, [_rest_transaction(_SALE_ORDER_ID, _SALE_ID, "sale", "success", _SALE_CREATED_AT)]
        )
        next_output = _read(config, {"created_at": state.created_at, "orders": dict(state.orders)})

    assert next_output.errors == []
    # `updated_at_min` is inclusive, so the order sharing the cursor value is read once more
    assert _emitted(next_output) == [(_SALE_ID, "success")]
