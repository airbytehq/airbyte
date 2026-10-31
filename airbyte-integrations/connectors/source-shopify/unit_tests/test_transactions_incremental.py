#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import orjson
from source_shopify.streams.streams import Orders, Transactions, TransactionsGraphql
from source_shopify.utils import EagerlyCachedStreamState as stream_state_cache

from airbyte_cdk.models import SyncMode


TRANSACTION_STATE = "2026-09-11T05:49:43+00:00"


def test_transactions_graphql_emits_transactions_older_than_state(requests_mock, bulk_job_completed_response, auth_config):
    stream_state_cache.cached_state.clear()
    stream = TransactionsGraphql(auth_config)
    transactions = [
        {
            "id": "gid://shopify/OrderTransaction/101",
            "createdAt": "2026-09-11T05:07:00Z",
            "processedAt": "2026-09-11T05:07:00Z",
            "amount": "10.00",
            "gateway": "klarna",
        },
        {
            "id": "gid://shopify/OrderTransaction/102",
            "createdAt": "2026-09-11T06:30:00Z",
            "processedAt": "2026-09-11T06:30:00Z",
            "amount": "10.00",
            "gateway": "card",
        },
    ]
    jsonl_content = orjson.dumps(
        {
            "__typename": "Order",
            "id": "gid://shopify/Order/123",
            "currency": "USD",
            "transactions": transactions,
        }
    ).decode()
    result_url = bulk_job_completed_response["data"]["node"]["url"]
    requests_mock.post(stream.job_manager.base_url, json=bulk_job_completed_response)
    requests_mock.get(result_url, text=f"{jsonl_content}\n")
    stream_state_cache.cached_state[stream.name] = {"created_at": TRANSACTION_STATE}

    records = list(stream.read_records(sync_mode=SyncMode.incremental, stream_slice={}))

    assert {record["id"] for record in records} == {101, 102}


def test_transactions_rest_emits_transactions_older_than_state(requests_mock, auth_config):
    stream_state_cache.cached_state.clear()
    stream = Transactions(auth_config)
    state = {"created_at": TRANSACTION_STATE, "orders": {"updated_at": TRANSACTION_STATE}}
    requests_mock.get(
        f"{stream.url_base}orders.json",
        json={"orders": [{"id": 123, "created_at": "2026-09-11T06:00:00+00:00", "updated_at": "2026-09-11T06:27:00+00:00"}]},
    )
    requests_mock.get(f"{stream.url_base}events.json", json={"events": []})
    requests_mock.get(
        f"{stream.url_base}orders/123/transactions.json",
        json={
            "transactions": [
                {"id": 101, "created_at": "2026-09-11T05:07:00+00:00", "amount": "10.00", "gateway": "klarna"},
                {"id": 102, "created_at": "2026-09-11T06:30:00+00:00", "amount": "10.00", "gateway": "card"},
            ]
        },
    )

    slices = list(stream.stream_slices(stream_state=state, sync_mode=SyncMode.incremental))
    records = [
        record
        for stream_slice in slices
        for record in stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice, stream_state=state)
    ]

    assert {record["id"] for record in records} == {101, 102}


def test_other_incremental_streams_still_drop_records_older_than_state(auth_config):
    stream = Orders(auth_config)
    records = list(
        stream.filter_records_newer_than_state(
            {"updated_at": TRANSACTION_STATE},
            [
                {"id": 1, "updated_at": "2026-09-11T05:07:00+00:00"},
                {"id": 2, "updated_at": "2026-09-11T06:30:00+00:00"},
            ],
        )
    )

    assert [record["id"] for record in records] == [2]
