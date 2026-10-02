# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the streams added for market parity:

- every stream logs in once with the shared token request for all read scopes, even across partitions
- list streams paginate with `start`/`page_size`, and the partitioned ones read every partition
- `business` and `business_balance` read Ramp's single-object responses
- `vendor_contacts` is read per vendor and carries `vendor_id`
- `vendor_agreements` is read through Ramp's POST query endpoint, paginating in the JSON body
- `receipts` is incremental on `created_at` via `created_after`
- missing-scope and plan-gated errors fail the stream as `config_error`, naming the stream's scope
"""

import json
from urllib.parse import parse_qs

import pytest
import requests_mock
from _helpers import (
    ALL_SCOPES,
    BASE_URL,
    CONFIG,
    START_DATE,
    TOKEN_RESPONSE,
    TOKEN_URL,
    get_source,
    query_params,
    read_stream,
    record_ids,
    requests_to,
)

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


TOKEN_PATH = "/developer/v1/token"


def _page(records: list, next_url=None) -> dict:
    return {"data": records, "page": {"next": next_url}}


def _token_scopes(request_history) -> list:
    return [parse_qs(request.text)["scope"][0] for request in requests_to(request_history, TOKEN_PATH)]


# (stream, endpoint path, scope, partition field, partition values)
LIST_STREAMS = [
    ("departments", "departments", "departments:read", None, None),
    ("locations", "locations", "locations:read", None, None),
    ("entities", "entities", "entities:read", None, None),
    ("funds", "funds", "funds:read", "is_terminated", ["false", "true"]),
    ("spend_programs", "spend-programs", "spend_programs:read", None, None),
    ("bills", "bills", "bills:read", "is_archived", ["false", "true"]),
    ("vendors", "vendors", "vendors:read", None, None),
    ("merchants", "merchants", "merchants:read", None, None),
    ("purchase_orders", "purchase-orders", "purchase_orders:read", None, None),
]


def test_discover_lists_every_stream():
    """Discover exposes the original three streams and all fifteen parity streams."""
    stream_names = {stream.name for stream in get_source(CONFIG).streams(CONFIG)}
    assert stream_names == {
        "cards",
        "transactions",
        "reimbursements",
        "users",
        "departments",
        "locations",
        "entities",
        "business",
        "business_balance",
        "funds",
        "spend_programs",
        "bills",
        "vendors",
        "vendor_contacts",
        "vendor_agreements",
        "receipts",
        "merchants",
        "purchase_orders",
    }


@pytest.mark.parametrize(
    "stream_name, path, scope, partition_field, partition_values",
    [pytest.param(*stream, id=stream[0]) for stream in LIST_STREAMS],
)
def test_list_stream_reads_with_its_own_scope(stream_name, path, scope, partition_field, partition_values):
    """Each list stream logs in for its own scope, paginates, and reads every partition."""
    url = f"{BASE_URL}/{path}"
    partitions = partition_values or [None]
    responses = []
    for index, _ in enumerate(partitions):
        responses.append({"json": _page([{"id": f"{stream_name}-{index}-a"}], next_url=f"{url}?start=x"), "status_code": 200})
        responses.append({"json": _page([{"id": f"{stream_name}-{index}-b"}]), "status_code": 200})

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(url, responses)
        output = read_stream(stream_name)

    assert not output.errors, f"expected a clean read, got {[error.trace.error.message for error in output.errors]}"
    assert len(record_ids(output)) == 2 * len(partitions)
    assert _token_scopes(mocker.request_history) == [ALL_SCOPES], "expected one login for every partition"

    data_requests = requests_to(mocker.request_history, f"/developer/v1/{path}")
    assert len(data_requests) == 2 * len(partitions)
    all_params = [query_params(request) for request in data_requests]
    assert all(params.get("page_size") == "50" for params in all_params)
    assert [params.get("start") for params in all_params[1::2]] == [f"{stream_name}-{index}-a" for index in range(len(partitions))]
    if partition_field:
        assert sorted({params[partition_field] for params in all_params}) == sorted(partition_values)


def test_users_read_unfiltered_then_suspended():
    """`users` makes one call without `status`, which returns every status except suspended, then one for suspended users.

    The `status` filter rejects the invite and onboarding statuses with 422, so per-status partitions would miss them.
    """
    url = f"{BASE_URL}/users"
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(
            url,
            [
                {"json": _page([{"id": "u-1", "status": "INVITE_PENDING"}]), "status_code": 200},
                {"json": _page([{"id": "u-2", "status": "USER_SUSPENDED"}]), "status_code": 200},
            ],
        )
        output = read_stream("users")

    assert not output.errors
    assert sorted(record_ids(output)) == ["u-1", "u-2"]
    statuses = [query_params(request).get("status") for request in requests_to(mocker.request_history, "/developer/v1/users")]
    assert sorted(statuses, key=str) == sorted([None, "USER_SUSPENDED"], key=str)


@pytest.mark.parametrize(
    "stream_name, path, flag",
    [
        pytest.param("vendors", "vendors", "include_subsidiary", id="vendors_subsidiary"),
        pytest.param("receipts", "receipts", "include_ocr_data", id="receipts_ocr"),
    ],
)
def test_optional_fields_are_requested(stream_name, path, flag):
    """Ramp only returns `subsidiary` and `ocr` when asked; the streams ask so those fields are populated."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(f"{BASE_URL}/{path}", json=_page([{"id": "x-1", "created_at": "2024-07-01T00:00:00+00:00"}]))
        read_stream(stream_name)

    assert query_params(requests_to(mocker.request_history, f"/developer/v1/{path}")[0]).get(flag) == "true"


def test_purchase_orders_include_archived():
    """`purchase_orders` asks for archived purchase orders so deletions replicate."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(f"{BASE_URL}/purchase-orders", json=_page([{"id": "po-1", "archived_at": "2024-06-01T00:00:00+00:00"}]))
        output = read_stream("purchase_orders")

    assert record_ids(output) == ["po-1"]
    params = query_params(requests_to(mocker.request_history, "/developer/v1/purchase-orders")[0])
    assert params.get("include_archived") == "true"


@pytest.mark.parametrize(
    "stream_name, path, record",
    [
        pytest.param("business", "business", {"id": "biz-1", "business_name_legal": "Acme"}, id="business"),
        pytest.param("business_balance", "business/balance", {"card_limit": 100000.0, "statement_balance": 250.0}, id="business_balance"),
    ],
)
def test_single_object_streams(stream_name, path, record):
    """Ramp returns these resources as one bare object; each read emits it as a single record."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(f"{BASE_URL}/{path}", json=record)
        output = read_stream(stream_name)

    assert [message.record.data for message in output.records] == [record]
    assert _token_scopes(mocker.request_history) == [ALL_SCOPES]
    assert len(requests_to(mocker.request_history, f"/developer/v1/{path}")) == 1


def test_vendor_contacts_are_read_per_vendor_and_carry_vendor_id():
    """`vendor_contacts` reads each vendor's contacts and adds the parent `vendor_id` to every record."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(f"{BASE_URL}/vendors", json=_page([{"id": "v-1"}, {"id": "v-2"}]))
        mocker.get(f"{BASE_URL}/vendors/v-1/contacts", json=_page([{"id": "c-1", "email": "a@example.com"}]))
        mocker.get(f"{BASE_URL}/vendors/v-2/contacts", json=_page([{"id": "c-1", "email": "b@example.com"}]))
        output = read_stream("vendor_contacts")

    records = sorted((message.record.data["vendor_id"], message.record.data["id"]) for message in output.records)
    assert records == [("v-1", "c-1"), ("v-2", "c-1")]
    # The parent `vendors` read builds its own authenticator, so the substream logs in twice.
    assert _token_scopes(mocker.request_history) == [ALL_SCOPES, ALL_SCOPES]


def test_vendor_contacts_skip_a_vendor_that_returns_404():
    """A vendor deleted between the parent read and its contacts call returns 404; the stream skips it and keeps going."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(f"{BASE_URL}/vendors", json=_page([{"id": "v-1"}, {"id": "v-2"}]))
        mocker.get(
            f"{BASE_URL}/vendors/v-1/contacts",
            json={"error_v2": {"error_code": "DEVELOPER_7002", "message": "The requested Vendor (v-1) does not exist"}},
            status_code=404,
        )
        mocker.get(f"{BASE_URL}/vendors/v-2/contacts", json=_page([{"id": "c-1", "email": "b@example.com"}]))
        output = read_stream("vendor_contacts")

    assert not output.errors
    assert [(message.record.data["vendor_id"], message.record.data["id"]) for message in output.records] == [("v-2", "c-1")]


def test_vendor_contacts_keep_the_scope_message_on_403():
    """The 404 handler does not swallow other errors: a 403 still fails the stream with the scope message."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(f"{BASE_URL}/vendors", json=_page([{"id": "v-1"}]))
        mocker.get(f"{BASE_URL}/vendors/v-1/contacts", json={"error_v2": {"error_code": "DEVELOPER_7999"}}, status_code=403)
        output = read_stream("vendor_contacts")

    errors = [message.trace.error for message in output.errors]
    assert errors and errors[0].failure_type == FailureType.config_error
    assert "vendors:read scope" in errors[0].message


def test_vendor_agreements_paginate_in_the_json_body():
    """`vendor_agreements` POSTs its query, asks for archived agreements, and pages with `start` in the body."""
    url = f"{BASE_URL}/vendors/agreements"
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.post(
            url,
            [
                {"json": _page([{"id": "agr-1"}], next_url=url), "status_code": 200},
                {"json": _page([{"id": "agr-2"}]), "status_code": 200},
            ],
        )
        output = read_stream("vendor_agreements")

    assert record_ids(output) == ["agr-1", "agr-2"]
    assert _token_scopes(mocker.request_history) == [ALL_SCOPES]
    bodies = [json.loads(request.text) for request in requests_to(mocker.request_history, "/developer/v1/vendors/agreements")]
    assert bodies == [
        {"include_archived": True, "page_size": 50},
        {"include_archived": True, "page_size": 50, "start": "agr-1"},
    ]


def test_receipts_incremental_on_created_at():
    """`receipts` sends the state cursor as `created_after` and advances the state to the newest `created_at`."""
    state = StateBuilder().with_stream_state("receipts", {"created_at": "2024-06-01T00:00:00Z"}).build()
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(f"{BASE_URL}/receipts", json=_page([{"id": "rc-1", "created_at": "2024-07-01T00:00:00+00:00"}]))
        output = read_stream("receipts", sync_mode=SyncMode.incremental, state=state)

    assert record_ids(output) == ["rc-1"]
    params = query_params(requests_to(mocker.request_history, "/developer/v1/receipts")[0])
    assert params.get("created_after") == "2024-06-01T00:00:00Z"
    assert output.most_recent_state.stream_state.__dict__.get("created_at", "").startswith("2024-07-01")


def test_receipts_first_sync_starts_at_start_date():
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(f"{BASE_URL}/receipts", json=_page([]))
        read_stream("receipts", sync_mode=SyncMode.incremental)

    params = query_params(requests_to(mocker.request_history, "/developer/v1/receipts")[0])
    assert params.get("created_after") == START_DATE


@pytest.mark.parametrize(
    "stream_name, path, error_code, expected_messages",
    [
        pytest.param("users", "users", "DEVELOPER_7100", ["grant the missing read scope"], id="missing_scope"),
        pytest.param("bills", "bills", "DEVELOPER_7999", ["bills:read scope"], id="generic_forbidden_names_scope"),
        pytest.param(
            "purchase_orders",
            "purchase-orders",
            "DEVELOPER_7999",
            ["purchase_orders:read scope", "only available on Ramp Plus"],
            id="purchase_orders_plan_gated",
        ),
    ],
)
def test_forbidden_new_stream_is_config_error(stream_name, path, error_code, expected_messages):
    """A 403 on a new stream fails it as `config_error`, never as zero records, and tells the user what to fix."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(
            f"{BASE_URL}/{path}",
            json={"error_v2": {"error_code": error_code, "message": "missing scope"}},
            status_code=403,
        )
        output = read_stream(stream_name)

    assert not output.records
    errors = [message.trace.error for message in output.errors]
    assert errors, "expected the read to emit an error trace"
    assert errors[0].failure_type == FailureType.config_error, f"expected config_error, got {errors[0].failure_type}"
    for expected in expected_messages:
        assert expected in errors[0].message, f"expected {expected!r} in {errors[0].message!r}"

