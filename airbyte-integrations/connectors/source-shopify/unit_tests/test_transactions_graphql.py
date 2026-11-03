#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from typing import List

import pytest
from source_shopify.streams.streams import TransactionsGraphql
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache

from airbyte_cdk.models import SyncMode


def _order_jsonl(order_id: int, transaction_id: int, transaction_created_at: str) -> str:
    return (
        f'{{"__typename":"Order","id":"gid:\\/\\/shopify\\/Order\\/{order_id}","currency":"USD",'
        f'"transactions":['
        f'{{"id":"gid:\\/\\/shopify\\/OrderTransaction\\/{transaction_id}","errorCode":null,"test":true,'
        f'"kind":"SALE","amount":"57.23","createdAt":"{transaction_created_at}","status":"SUCCESS",'
        f'"processedAt":"{transaction_created_at}","gateway":"bogus","paymentId":"c25048437719229.1",'
        f'"accountNumber":"1","formattedGateway":"bogus","manuallyCapturable":false,"receipt":"{{}}",'
        f'"parentTransaction":null,"authorization":null,'
        f'"totalUnsettledSet":{{"presentmentMoney":{{"amount":"0.0","currency":"USD"}},'
        f'"shopMoney":{{"amount":"0.0","currency":"USD"}}}},'
        f'"amountSet":{{"shop_money":{{"amount":"57.23","currency":"USD"}}}},"fees":[],"paymentDetails":{{}}'
        f"}}]}}"
    )


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

    return stream, records


def test_transactions_graphql_emits_transactions_predating_state(
    requests_mock,
    bulk_job_completed_response,
    auth_config,
) -> None:
    """Every transaction returned by the BULK job is emitted, whatever its own `created_at` is.

    The BULK job filters the parent `orders` on `updated_at`, so a transaction can only appear here if
    its order matched the requested window. Filtering the child on its own immutable `created_at` on top
    of that permanently drops transactions of orders that are updated after they were created.
    """
    _, test_records = _read_transactions(
        requests_mock,
        bulk_job_completed_response,
        auth_config,
        [
            # transaction predates the saved state, its order is newly created -> emitted
            _order_jsonl(1, 1001, "2026-09-11T05:07:00Z"),
            # transaction predates the saved state, its order was created long ago and only updated now -> emitted
            _order_jsonl(2, 1002, "2026-09-11T05:07:00Z"),
            # transaction is newer than the saved state -> emitted
            _order_jsonl(3, 1003, "2026-09-11T06:00:00Z"),
        ],
        state_value="2026-09-11T05:49:43+00:00",
    )

    assert sorted(record["id"] for record in test_records) == [1001, 1002, 1003]
    assert all("order_created_at" not in record for record in test_records)


def test_transactions_graphql_emits_transaction_of_order_re_touched_after_cursor_passed_it(
    requests_mock,
    bulk_job_completed_response,
    auth_config,
) -> None:
    """The core scenario of https://github.com/airbytehq/airbyte/issues/90842.

    An order created years ago is updated now (a refund, a capture, a late offsite checkout, or a
    historical backfill reaching it late), so it falls into the current BULK window on `updated_at`.
    Its transactions were created years ago, far behind the saved `created_at` cursor, and some of them
    were never emitted. They must still be emitted: `created_at` never changes, so no later sync at any
    state could ever recover them.
    """
    _, test_records = _read_transactions(
        requests_mock,
        bulk_job_completed_response,
        auth_config,
        [_order_jsonl(4554821468349, 1001, "2021-03-02T10:15:00Z")],
        state_value="2026-09-11T05:49:43+00:00",
    )

    assert [record["id"] for record in test_records] == [1001]
    assert test_records[0]["created_at"] == "2021-03-02T10:15:00+00:00"


def test_transactions_graphql_re_emission_does_not_move_the_cursor_backwards(
    requests_mock,
    bulk_job_completed_response,
    auth_config,
) -> None:
    """Emitting records older than the state must not regress the saved state.

    `get_updated_state` keeps the maximum cursor value seen, so the extra, older records rescued by
    `should_emit_record_older_than_state` can never pull the cursor back. The re-emission itself is the
    accepted trade-off: the records are immutable and keyed by `id`, so they upsert idempotently.
    """
    # the transaction predates the saved state and is re-emitted on every sync that returns its order
    predating_order = _order_jsonl(1, 1001, "2026-09-11T05:07:00Z")
    # a later transaction on another order, which is what actually advances the cursor
    newer_order = _order_jsonl(2, 1002, "2026-09-11T06:31:00Z")
    syncs = [
        ([predating_order], [1001]),
        ([predating_order, newer_order], [1001, 1002]),
        # the cursor has moved past the predating transaction, it is still emitted
        ([predating_order, newer_order], [1001, 1002]),
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
    "state_value",
    [
        pytest.param("2026-09-11T05:49:43+00:00", id="state_after_the_transaction"),
        pytest.param("2021-01-01T00:00:00+00:00", id="state_before_the_transaction"),
    ],
)
def test_transactions_graphql_emits_the_same_records_regardless_of_state(
    requests_mock,
    bulk_job_completed_response,
    auth_config,
    state_value,
) -> None:
    """The saved state no longer changes what a given BULK result emits for this stream.

    It still drives the slice boundaries in `stream_slices`, which is where incrementality for this
    stream now lives.
    """
    _, test_records = _read_transactions(
        requests_mock,
        bulk_job_completed_response,
        auth_config,
        [_order_jsonl(1, 1001, "2026-09-11T05:07:00Z")],
        state_value=state_value,
    )

    assert [record["id"] for record in test_records] == [1001]
