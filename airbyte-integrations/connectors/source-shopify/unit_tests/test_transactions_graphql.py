#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from typing import List, Optional

import pytest
from source_shopify.streams.streams import TransactionsGraphql
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache

from airbyte_cdk.models import SyncMode


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


@pytest.mark.parametrize(
    "order_jsonl, expected_ids",
    [
        pytest.param(
            # the refund and its order predate the saved state, the order was updated after it (refund PENDING -> SUCCESS)
            _order_jsonl(1, "2026-10-20T08:00:00Z", 1001, "2026-10-21T09:00:00Z", order_updated_at="2026-10-22T15:10:00Z", kind="REFUND"),
            [1001],
            id="order_updated_after_state_is_emitted",
        ),
        pytest.param(
            _order_jsonl(1, "2026-10-20T08:00:00Z", 1001, "2026-10-21T09:00:00Z", order_updated_at="2026-10-22T14:59:10Z", kind="REFUND"),
            [1001],
            id="order_updated_at_equal_to_state_is_emitted",
        ),
        pytest.param(
            _order_jsonl(1, "2026-10-20T08:00:00Z", 1001, "2026-10-21T09:00:00Z", order_updated_at="2026-10-22T14:00:00Z", kind="REFUND"),
            [],
            id="order_updated_before_state_is_dropped",
        ),
    ],
)
def test_transactions_graphql_emits_transactions_of_orders_updated_after_state(
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
        state_value="2026-10-22T14:59:10+00:00",
    )

    assert [record["id"] for record in test_records] == expected_ids
    assert all("order_updated_at" not in record for record in test_records)


def test_transactions_graphql_refund_status_change_is_captured_incrementally(
    requests_mock,
    bulk_job_completed_response,
    auth_config,
) -> None:
    state = {"created_at": "2026-10-22T14:16:17+00:00"}
    pending = _order_jsonl(
        1, "2026-10-20T08:00:00Z", 1001, "2026-10-22T14:00:00Z", order_updated_at="2026-10-22T14:00:00Z", kind="REFUND", status="PENDING"
    )
    newer_sale = _order_jsonl(2, "2026-10-22T14:59:00Z", 1002, "2026-10-22T14:59:10Z", order_updated_at="2026-10-22T14:59:10Z")
    succeeded = _order_jsonl(
        1, "2026-10-20T08:00:00Z", 1001, "2026-10-22T14:00:00Z", order_updated_at="2026-10-22T15:10:00Z", kind="REFUND", status="SUCCESS"
    )

    stream, first_sync = _read_transactions(
        requests_mock, bulk_job_completed_response, auth_config, [pending, newer_sale], state_value=state["created_at"]
    )
    assert [record["id"] for record in first_sync] == [1002]
    for record in first_sync:
        state = stream.get_updated_state(state, record)
    assert state == {"created_at": "2026-10-22T14:59:10+00:00"}

    _, second_sync = _read_transactions(
        requests_mock, bulk_job_completed_response, auth_config, [succeeded], state_value=state["created_at"]
    )
    assert [(record["id"], record["status"]) for record in second_sync] == [(1001, "SUCCESS")]
