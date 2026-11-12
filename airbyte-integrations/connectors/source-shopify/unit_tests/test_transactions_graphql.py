#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from typing import List

import pytest
from source_shopify.streams.streams import TransactionsGraphql
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache

from airbyte_cdk.models import SyncMode


def _order_jsonl(order_id: int, order_created_at: str, transaction_id: int, transaction_created_at: str) -> str:
    return (
        f'{{"__typename":"Order","id":"gid:\\/\\/shopify\\/Order\\/{order_id}","currency":"USD",'
        f'"order_created_at":"{order_created_at}","transactions":['
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


_STATE_VALUE = "2026-09-11T05:49:43+00:00"
# the transaction predates the saved state, its order is part of the BULK job result since it was updated after that state
_TRANSACTION_OLDER_THAN_STATE = "2026-09-11T05:07:00Z"


@pytest.mark.parametrize(
    "order_jsonl",
    [
        pytest.param(
            _order_jsonl(1, "2026-09-11T04:00:00Z", 1001, _TRANSACTION_OLDER_THAN_STATE),
            id="order_created_before_state",
        ),
        pytest.param(
            _order_jsonl(1, "2026-09-11T06:27:00Z", 1001, _TRANSACTION_OLDER_THAN_STATE),
            id="order_created_after_state",
        ),
        pytest.param(
            _order_jsonl_without_order_created_at(
                _order_jsonl(1, "2026-09-11T06:27:00Z", 1001, _TRANSACTION_OLDER_THAN_STATE), keep_key_as_null=False
            ),
            id="missing_order_created_at",
        ),
        pytest.param(
            _order_jsonl_without_order_created_at(
                _order_jsonl(1, "2026-09-11T06:27:00Z", 1001, _TRANSACTION_OLDER_THAN_STATE), keep_key_as_null=True
            ),
            id="null_order_created_at",
        ),
    ],
)
def test_transactions_graphql_emits_transactions_older_than_state_without_order_created_at(
    requests_mock,
    bulk_job_completed_response,
    auth_config,
    order_jsonl,
) -> None:
    stream, test_records = _read_transactions(
        requests_mock,
        bulk_job_completed_response,
        auth_config,
        [order_jsonl],
        state_value=_STATE_VALUE,
    )

    assert [record["id"] for record in test_records] == [1001]
    # the cursor never moves backwards when an older transaction is emitted
    assert stream.get_updated_state({"created_at": _STATE_VALUE}, test_records[0]) == {"created_at": _STATE_VALUE}
