#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from typing import List

from source_shopify.streams.streams import Transactions, TransactionsGraphql
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache

from airbyte_cdk.models import SyncMode


def _order_jsonl(order_id: int, transaction_id: int, transaction_created_at: str, status: str = "SUCCESS") -> str:
    return (
        f'{{"__typename":"Order","id":"gid:\\/\\/shopify\\/Order\\/{order_id}","currency":"USD","transactions":['
        f'{{"id":"gid:\\/\\/shopify\\/OrderTransaction\\/{transaction_id}","errorCode":null,"test":true,'
        f'"kind":"REFUND","amount":"57.23","createdAt":"{transaction_created_at}","status":"{status}",'
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


def test_transactions_graphql_emits_status_change_of_transaction_predating_state(
    requests_mock,
    bulk_job_completed_response,
    auth_config,
) -> None:
    # the BULK query is filtered by the order `updated_at`, so the order of the refund comes back
    # on the second sync only because the refund moved from PENDING to SUCCESS
    pending_refund = _order_jsonl(1, 1001, "2026-09-11T05:07:00Z", status="PENDING")
    settled_refund = _order_jsonl(1, 1001, "2026-09-11T05:07:00Z", status="SUCCESS")
    newer_order = _order_jsonl(2, 1002, "2026-09-11T05:49:43Z")
    syncs = [
        ([pending_refund, newer_order], [(1001, "PENDING"), (1002, "SUCCESS")]),
        # the refund predates the saved state, it is emitted again with its new status
        ([settled_refund], [(1001, "SUCCESS")]),
    ]

    state = {"created_at": "2026-09-11T04:30:00+00:00"}
    for jsonl_lines, expected_records in syncs:
        stream, test_records = _read_transactions(
            requests_mock,
            bulk_job_completed_response,
            auth_config,
            jsonl_lines,
            state_value=state["created_at"],
        )
        assert [(record["id"], record["status"]) for record in test_records] == expected_records

        for record in test_records:
            state = stream.get_updated_state(state, record)
        # the cursor does not move backwards when an older transaction is emitted again
        assert state == {"created_at": "2026-09-11T05:49:43+00:00"}


def test_transactions_rest_emits_status_change_of_transaction_predating_state(requests_mock, auth_config) -> None:
    stream = Transactions(auth_config)
    transactions = [
        {"id": 1001, "order_id": 1, "kind": "refund", "status": "success", "created_at": "2026-09-11T05:07:00+00:00"},
        {"id": 1003, "order_id": 1, "kind": "sale", "status": "success", "created_at": "2026-09-11T06:00:00+00:00"},
    ]
    requests_mock.get(f"{stream.url_base}orders/1/transactions.json", json={"transactions": transactions})

    stream_state_cache.cached_state["transactions"] = {"created_at": "2026-09-11T05:49:43+00:00"}
    try:
        test_records = list(stream.read_records(sync_mode=SyncMode.incremental, stream_slice={"order_id": 1}))
    finally:
        stream_state_cache.cached_state.pop("transactions", None)

    assert [(record["id"], record["status"]) for record in test_records] == [(1001, "success"), (1003, "success")]
