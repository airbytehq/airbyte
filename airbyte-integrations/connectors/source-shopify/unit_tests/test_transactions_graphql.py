#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from typing import List, Optional

import pytest
from freezegun import freeze_time
from source_shopify import SourceShopify
from source_shopify.scopes import SCOPES_MAPPING
from source_shopify.streams.base_streams import ShopifyStream
from source_shopify.streams.streams import TransactionsGraphql
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _order_jsonl(
    order_id: int,
    order_created_at: str,
    transaction_id: int,
    transaction_created_at: str,
    order_updated_at: Optional[str] = None,
    kind: str = "SALE",
    status: str = "SUCCESS",
) -> str:
    order_updated_at_field = f'"order_updated_at":"{order_updated_at}",' if order_updated_at else ""
    return (
        f'{{"__typename":"Order","id":"gid:\\/\\/shopify\\/Order\\/{order_id}","currency":"USD",'
        f'"order_created_at":"{order_created_at}",{order_updated_at_field}"transactions":['
        f'{{"id":"gid:\\/\\/shopify\\/OrderTransaction\\/{transaction_id}","errorCode":null,"test":true,'
        f'"kind":"{kind}","amount":"57.23","createdAt":"{transaction_created_at}","status":"{status}",'
        f'"processedAt":"{transaction_created_at}","gateway":"bogus","paymentId":"c25048437719229.1",'
        f'"accountNumber":"1","formattedGateway":"bogus","manuallyCapturable":false,"receipt":"{{}}",'
        f'"parentTransaction":null,"authorization":null,'
        f'"totalUnsettledSet":{{"presentmentMoney":{{"amount":"0.0","currency":"USD"}},'
        f'"shopMoney":{{"amount":"0.0","currency":"USD"}}}},'
        f'"amountSet":{{"shop_money":{{"amount":"57.23","currency":"USD"}}}},"fees":[],"paymentDetails":{{}}'
        f"}}]}}"
    )


def test_transactions_graphql_emits_transactions_predating_state_with_new_order(
    requests_mock,
    bulk_job_completed_response,
    auth_config,
) -> None:
    stream = TransactionsGraphql(auth_config)
    test_result_url = bulk_job_completed_response.get("data").get("node").get("url")

    jsonl_content = (
        "\n".join(
            [
                # transaction predates the saved state, but its order is newer -> emitted
                _order_jsonl(1, "2026-09-11T06:27:00Z", 1001, "2026-09-11T05:07:00Z"),
                # transaction and its order both predate the saved state -> dropped
                _order_jsonl(2, "2026-09-11T04:00:00Z", 1002, "2026-09-11T05:07:00Z"),
                # transaction is newer than the saved state even though its order is older -> emitted
                _order_jsonl(3, "2026-09-11T04:00:00Z", 1003, "2026-09-11T06:00:00Z"),
            ]
        )
        + "\n"
    )

    requests_mock.post(stream.job_manager.base_url, json=bulk_job_completed_response)
    requests_mock.get(test_result_url, text=jsonl_content)

    stream_state_cache.cached_state["transactions"] = {"created_at": "2026-09-11T05:49:43+00:00"}
    try:
        test_records = list(stream.read_records(SyncMode.incremental, stream_slice={}))
    finally:
        stream_state_cache.cached_state.pop("transactions", None)

    assert sorted(record["id"] for record in test_records) == [1001, 1003]
    assert all("order_created_at" not in record for record in test_records)


def _order_jsonl_without_order_created_at(order_jsonl: str, keep_key_as_null: bool) -> str:
    order = json.loads(order_jsonl)
    if keep_key_as_null:
        order["order_created_at"] = None
    else:
        order.pop("order_created_at")
    return json.dumps(order)


def _read_transactions(requests_mock, bulk_job_completed_response, auth_config, jsonl_lines: List[str], state_value: str):
    stream = TransactionsGraphql(auth_config)
    test_result_url = bulk_job_completed_response.get("data").get("node").get("url")
    requests_mock.post(stream.job_manager.base_url, json=bulk_job_completed_response)
    requests_mock.get(test_result_url, text="\n".join(jsonl_lines) + "\n")

    stream_state_cache.cached_state["transactions"] = {"created_at": state_value}
    try:
        records = list(stream.read_records(SyncMode.incremental, stream_slice={}))
    finally:
        stream_state_cache.cached_state.pop("transactions", None)

    assert all("order_created_at" not in record for record in records)
    return stream, records


@pytest.mark.parametrize(
    "order_jsonl, expected_ids",
    [
        pytest.param(
            _order_jsonl(1, "2026-09-11T05:49:43Z", 1001, "2026-09-11T05:07:00Z"),
            [1001],
            id="order_created_at_equal_to_state_is_emitted",
        ),
        pytest.param(
            _order_jsonl_without_order_created_at(
                _order_jsonl(1, "2026-09-11T06:27:00Z", 1001, "2026-09-11T05:07:00Z"), keep_key_as_null=False
            ),
            [],
            id="missing_order_created_at_is_dropped",
        ),
        pytest.param(
            _order_jsonl_without_order_created_at(
                _order_jsonl(1, "2026-09-11T06:27:00Z", 1001, "2026-09-11T05:07:00Z"), keep_key_as_null=True
            ),
            [],
            id="null_order_created_at_is_dropped",
        ),
    ],
)
def test_transactions_graphql_older_than_state_order_created_at_edge_cases(
    requests_mock,
    bulk_job_completed_response,
    auth_config,
    order_jsonl,
    expected_ids,
) -> None:
    _, test_records = _read_transactions(
        requests_mock,
        bulk_job_completed_response,
        auth_config,
        [order_jsonl],
        state_value="2026-09-11T05:49:43+00:00",
    )

    assert [record["id"] for record in test_records] == expected_ids


def test_transactions_graphql_re_emission_of_transactions_predating_order_is_bounded(
    requests_mock,
    bulk_job_completed_response,
    auth_config,
) -> None:
    # the transaction predates both the saved state and its order, the order is newer than the saved state
    predating_order = _order_jsonl(1, "2026-09-11T06:27:00Z", 1001, "2026-09-11T05:07:00Z")
    # a later transaction on another order, created after the first order
    newer_order = _order_jsonl(2, "2026-09-11T06:30:00Z", 1002, "2026-09-11T06:31:00Z")
    syncs = [
        ([predating_order], [1001]),
        # the cursor has not moved past the first order's createdAt yet -> re-emitted
        ([predating_order, newer_order], [1001, 1002]),
        # the cursor moved past the first order's createdAt -> no longer emitted
        ([predating_order, newer_order], [1002]),
    ]

    state = {"created_at": "2026-09-11T05:49:43+00:00"}
    for jsonl_lines, expected_ids in syncs:
        stream, test_records = _read_transactions(
            requests_mock,
            bulk_job_completed_response,
            auth_config,
            jsonl_lines,
            state_value=state["created_at"],
        )
        assert sorted(record["id"] for record in test_records) == expected_ids

        previous_state_value = state["created_at"]
        for record in test_records:
            state = stream.get_updated_state(state, record)
        assert state["created_at"] >= previous_state_value

    assert state == {"created_at": "2026-09-11T06:31:00+00:00"}


_SHOP_NAME = "airbyte-integration-test"
_GRAPHQL_URL = f"https://{_SHOP_NAME}.myshopify.com/admin/api/{ShopifyStream.api_version}/graphql.json"
_JOB_RESULT_URL = (
    'https://storage.example.com/bulk?response-content-disposition=attachment;+filename="bulk-123456789.jsonl";'
    "+filename*=UTF-8''bulk-123456789.jsonl&response-content-type=application/jsonl"
)
_BULK_OPERATION_ID = "gid://shopify/BulkOperation/4047052112061"


def _mock_bulk_job(requests_mock, jsonl_lines: List[str]):
    """Mock the shop, the BULK job creation, its status and its result file. Returns the job creation mock."""
    requests_mock.get(
        f"https://{_SHOP_NAME}.myshopify.com/admin/api/{ShopifyStream.api_version}/shop.json",
        json={"shop": {"id": 1, "myshopify_domain": f"{_SHOP_NAME}.myshopify.com"}},
    )
    requests_mock.get(
        f"https://{_SHOP_NAME}.myshopify.com/admin/oauth/access_scopes.json",
        json={"access_scopes": [{"handle": scope} for scopes in SCOPES_MAPPING.values() for scope in scopes]},
    )
    job_creation = requests_mock.post(
        _GRAPHQL_URL,
        additional_matcher=lambda request: "bulkOperationRunQuery" in request.text,
        json={
            "data": {
                "bulkOperationRunQuery": {
                    "bulkOperation": {"id": _BULK_OPERATION_ID, "status": "CREATED", "createdAt": "2026-10-22T16:00:00Z"},
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
                    "id": _BULK_OPERATION_ID,
                    "status": "COMPLETED",
                    "errorCode": None,
                    "createdAt": "2026-10-22T16:00:00Z",
                    "objectCount": str(len(jsonl_lines)),
                    "fileSize": "774",
                    "url": _JOB_RESULT_URL,
                    "partialDataUrl": None,
                }
            }
        },
    )
    requests_mock.get(_JOB_RESULT_URL, text="\n".join(jsonl_lines) + "\n")
    return job_creation


def _read_transactions_incrementally(requests_mock, jsonl_lines: List[str], state: dict):
    # the stream state cache lives at the class level, a new sync always starts with an empty one
    stream_state_cache.cached_state.clear()
    job_creation = _mock_bulk_job(requests_mock, jsonl_lines)
    config = {
        "start_date": "2026-01-01",
        "shop": _SHOP_NAME,
        "credentials": {"auth_method": "api_password", "api_password": "api_password"},
    }
    catalog = CatalogBuilder().with_stream("transactions", SyncMode.incremental).build()
    try:
        output = read(SourceShopify(), config, catalog, state=StateBuilder().with_stream_state("transactions", state).build())
    finally:
        stream_state_cache.cached_state.clear()
    assert output.errors == []
    return output, job_creation.last_request.json()["query"]


@freeze_time("2026-10-22T16:01:00+00:00")
def test_transactions_graphql_emits_status_change_of_existing_transaction_when_its_order_is_updated(requests_mock) -> None:
    """
    A refund created as PENDING becomes SUCCESS later on: Shopify keeps the transaction `createdAt` and only
    bumps the parent order `updatedAt`. The updated transaction should reach the destination on the next
    incremental sync, even though both the transaction and its order were created before the saved state.
    """
    # order and refund were created before the saved state, the refund became SUCCESS after it
    settled_refund = _order_jsonl(
        1, "2026-10-22T13:00:00Z", 1001, "2026-10-22T13:30:00Z", order_updated_at="2026-10-22T15:05:00Z", kind="REFUND"
    )
    # order and transaction were created after the saved state
    new_order = _order_jsonl(2, "2026-10-22T15:10:00Z", 1002, "2026-10-22T15:11:00Z", order_updated_at="2026-10-22T15:11:00Z")

    first_sync, first_query = _read_transactions_incrementally(
        requests_mock, [settled_refund, new_order], state={"created_at": "2026-10-22T14:59:10+00:00"}
    )

    assert "updated_at:>='2026-10-22T14:59:10+00:00' AND updated_at:<='2026-10-22T16:01:00+00:00'" in first_query
    assert [(record.record.data["id"], record.record.data["status"]) for record in first_sync.records] == [
        (1001, "SUCCESS"),
        (1002, "SUCCESS"),
    ]
    assert all(
        "order_updated_at" not in record.record.data and "order_created_at" not in record.record.data for record in first_sync.records
    )
    # the order `updatedAt` drives the emission above, so it has to be requested
    assert "order_updated_at: updatedAt" in first_query
    first_state = first_sync.most_recent_state.stream_state.__dict__
    assert first_state == {"created_at": "2026-10-22T15:11:00+00:00"}

    # the cursor moved past the first order's `updatedAt`: the settled refund is not repeated,
    # only the transaction sitting on the (inclusive) cursor value is.
    second_sync, second_query = _read_transactions_incrementally(requests_mock, [settled_refund, new_order], state=first_state)

    assert "updated_at:>='2026-10-22T15:11:00+00:00' AND updated_at:<='2026-10-22T16:01:00+00:00'" in second_query
    assert [record.record.data["id"] for record in second_sync.records] == [1002]
    assert second_sync.most_recent_state.stream_state.__dict__ == first_state
