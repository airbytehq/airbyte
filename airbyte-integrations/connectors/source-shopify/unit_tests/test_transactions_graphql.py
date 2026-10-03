#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


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
