# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-ramp` covering the manifest behaviours that are easy to regress:

- the `SessionTokenAuthenticator` login call (HTTP Basic client credentials, form body with the
  read scopes) and the `Bearer` token it hands to the data requests
- `DefaultPaginator` + `CursorPagination`: `page_size` on every request, `start` set to the `id`
  of the previous page's last record, and a null-safe stop condition
- `transactions` incremental sync is filtered server-side via `updated_after`, and every request
  sends `state=ALL` so declined transactions are included
- `cards` is read once per `is_terminated` value so terminated cards are included
- Ramp's auth and scope errors surface as `config_error` with an actionable message
- `reimbursements` incremental sync is filtered server-side via `updated_after`, once per
  `direction` partition
"""

import base64
import logging
from urllib.parse import parse_qs

import pytest
import requests_mock
from _helpers import (
    ACCESS_TOKEN,
    CARDS_URL,
    CONFIG,
    REIMBURSEMENTS_URL,
    START_DATE,
    TOKEN_RESPONSE,
    TOKEN_URL,
    TRANSACTIONS_URL,
    get_source,
    query_params,
    read_stream,
    record_ids,
    requests_to,
)

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


TOKEN_PATH = "/developer/v1/token"
CARDS_PATH = "/developer/v1/cards"
TRANSACTIONS_PATH = "/developer/v1/transactions"
REIMBURSEMENTS_PATH = "/developer/v1/reimbursements"

EXPECTED_SCOPE = "transactions:read cards:read reimbursements:read"


def _card(card_id: str) -> dict:
    return {"id": card_id, "display_name": "Card", "state": "ACTIVE", "is_physical": True}


def _transaction(transaction_id: str, updated_at: str) -> dict:
    return {
        "id": transaction_id,
        "amount": 90.0,
        "state": "CLEARED",
        "updated_at": updated_at,
        "user_transaction_time": "2024-05-28T00:00:00+00:00",
    }


def _reimbursement(reimbursement_id: str, direction: str, updated_at: str = "2024-06-01T00:00:00+00:00") -> dict:
    return {
        "id": reimbursement_id,
        "amount": 25.0,
        "direction": direction,
        "state": "REIMBURSED",
        "updated_at": updated_at,
    }


def _page(records: list, next_url=None) -> dict:
    """Ramp's list envelope: records under `data`, pagination under `page.next`."""
    return {"data": records, "page": {"next": next_url}}


def test_token_request():
    """Reading a stream logs in once with HTTP Basic client credentials and then sends `Bearer <token>`."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(TRANSACTIONS_URL, json=_page([_transaction("tx-1", "2024-06-01T00:00:00+00:00")]))
        output = read_stream("transactions")

    assert record_ids(output) == ["tx-1"]

    token_requests = requests_to(mocker.request_history, TOKEN_PATH)
    assert len(token_requests) == 1, f"expected exactly one login request, got {len(token_requests)}"
    login = token_requests[0]
    assert login.method == "POST"

    authorization = login.headers["Authorization"]
    assert authorization.startswith("Basic "), f"login must use HTTP Basic auth, got {authorization!r}"
    decoded = base64.b64decode(authorization.removeprefix("Basic ")).decode()
    assert decoded == f"{CONFIG['client_id']}:{CONFIG['client_secret']}"

    form_body = parse_qs(login.text)
    assert form_body["grant_type"] == ["client_credentials"]
    assert form_body["scope"] == [EXPECTED_SCOPE], f"login must request the three read scopes, got {form_body.get('scope')}"

    data_requests = requests_to(mocker.request_history, TRANSACTIONS_PATH)
    assert len(data_requests) == 1
    assert data_requests[0].headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"


def test_pagination():
    """`start` carries the `id` of the previous page's last record and `page_size` is sent on every page."""
    updated_at = "2024-06-01T00:00:00+00:00"
    page_1 = _page([_transaction("tx-1", updated_at), _transaction("tx-2", updated_at)], next_url=f"{TRANSACTIONS_URL}?start=tx-2")
    page_2 = _page([_transaction("tx-3", updated_at), _transaction("tx-4", updated_at)])

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(TRANSACTIONS_URL, [{"json": page_1, "status_code": 200}, {"json": page_2, "status_code": 200}])
        output = read_stream("transactions")

    assert record_ids(output) == ["tx-1", "tx-2", "tx-3", "tx-4"]

    data_requests = requests_to(mocker.request_history, TRANSACTIONS_PATH)
    assert len(data_requests) == 2, f"expected 2 paginated requests, got {len(data_requests)}"

    first_params = query_params(data_requests[0])
    assert first_params.get("page_size") == "50"
    assert "start" not in first_params, f"first request must not carry a page token, got {first_params}"

    second_params = query_params(data_requests[1])
    assert second_params.get("start") == "tx-2", f"second request must resume from the last record id, got {second_params}"
    assert second_params.get("page_size") == "50"


def test_pagination_stops_on_null_page():
    """A response whose `page` key is present but null must end the read instead of looping."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(
            TRANSACTIONS_URL,
            [
                {"json": {"data": [_transaction("tx-1", "2024-06-01T00:00:00+00:00")], "page": None}, "status_code": 200},
                # A stop condition that is not null-safe loops on the same page forever. Failing the
                # second request keeps that regression a fast test failure instead of a hung suite.
                {"json": {}, "status_code": 400},
            ],
        )
        output = read_stream("transactions")

    assert record_ids(output) == ["tx-1"]
    data_requests = requests_to(mocker.request_history, TRANSACTIONS_PATH)
    assert len(data_requests) == 1, f"expected the read to stop after one page, got {len(data_requests)} requests"


def test_transactions_server_side_incremental():
    """`transactions` sends the state cursor as `updated_after` and asks for every state, including declined."""
    state = StateBuilder().with_stream_state("transactions", {"updated_at": "2024-06-01T00:00:00Z"}).build()
    declined = {**_transaction("tx-declined", "2024-07-01T00:00:00+00:00"), "state": "DECLINED"}

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(TRANSACTIONS_URL, json=_page([_transaction("tx-new", "2024-07-01T00:00:00+00:00"), declined]))
        output = read_stream("transactions", sync_mode=SyncMode.incremental, state=state)

    assert record_ids(output) == ["tx-new", "tx-declined"]

    data_requests = requests_to(mocker.request_history, TRANSACTIONS_PATH)
    assert len(data_requests) == 1, f"expected one request against /transactions, got {len(data_requests)}"
    params = query_params(data_requests[0])
    assert params.get("updated_after") == "2024-06-01T00:00:00Z", f"expected the state cursor as `updated_after`, got {params}"
    assert params.get("state") == "ALL", f"transactions must request every state, got {params}"


def test_transactions_default_start_date():
    """Without `start_date` in the config, the first sync starts from the spec default."""
    config = {key: value for key, value in CONFIG.items() if key != "start_date"}

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(TRANSACTIONS_URL, json=_page([]))
        read_stream("transactions", config=config, sync_mode=SyncMode.incremental)

    params = query_params(requests_to(mocker.request_history, TRANSACTIONS_PATH)[0])
    assert params.get("updated_after") == "2019-01-01T00:00:00Z", f"expected the default start date, got {params}"


def test_cards_include_terminated():
    """`cards` is read once per `is_terminated` value so terminated cards reach the destination."""
    terminated = {**_card("card-2"), "state": "TERMINATED"}

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(CARDS_URL + "?is_terminated=false", json=_page([_card("card-1")]))
        mocker.get(CARDS_URL + "?is_terminated=true", json=_page([terminated]))
        output = read_stream("cards")

    assert sorted(record_ids(output)) == ["card-1", "card-2"]
    data_requests = requests_to(mocker.request_history, CARDS_PATH)
    assert sorted(query_params(request).get("is_terminated") for request in data_requests) == ["false", "true"]


@pytest.mark.parametrize(
    "status_code, error_code, expected_message",
    [
        pytest.param(403, "DEVELOPER_7100", "grant the missing read scope", id="missing_scope"),
        pytest.param(404, "DEVELOPER_7002", "no longer accepts this connector's access token", id="revoked_token"),
        pytest.param(401, "DEVELOPER_7000", "Re-enter the client ID and client secret", id="generic_unauthorized"),
        pytest.param(403, "DEVELOPER_7999", "transactions:read, cards:read and reimbursements:read", id="generic_forbidden"),
    ],
)
def test_data_request_auth_errors_are_config_errors(status_code, error_code, expected_message):
    """Ramp's auth and scope errors on data requests fail the sync as `config_error` with an actionable message."""
    body = {"error_v2": {"error_code": error_code, "message": "cards:read"}}

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(TRANSACTIONS_URL, json=body, status_code=status_code)
        output = read_stream("transactions")

    errors = [message.trace.error for message in output.errors]
    assert errors, "expected the read to emit an error trace"
    assert errors[0].failure_type == FailureType.config_error, f"expected config_error, got {errors[0].failure_type}"
    assert expected_message in errors[0].message, f"unexpected message {errors[0].message!r}"
    assert len(requests_to(mocker.request_history, TRANSACTIONS_PATH)) == 1, "auth errors must not be retried"


@pytest.mark.parametrize("status_code", [400, 401])
def test_login_errors_are_config_errors(status_code):
    """A rejected client ID or secret on the token call fails as `config_error` and quotes Ramp's reason."""
    body = {"error_v2": {"error_code": "5006", "message": "client_id is malformed, invalid length."}}

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=body, status_code=status_code)
        output = read_stream("transactions")

    errors = [message.trace.error for message in output.errors]
    assert errors, "expected the read to emit an error trace"
    assert errors[0].failure_type == FailureType.config_error, f"expected config_error, got {errors[0].failure_type}"
    assert "client_id is malformed" in errors[0].message, f"unexpected message {errors[0].message!r}"
    assert len(requests_to(mocker.request_history, TOKEN_PATH)) == 1, "login errors must not be retried"


def test_reimbursements_server_side_filter_and_directions():
    """`reimbursements` is read once per `direction`, each request filtered server-side by `updated_after`."""
    responses = [
        {"json": _page([_reimbursement("rb-1", "BUSINESS_TO_USER")]), "status_code": 200},
        {"json": _page([_reimbursement("rb-2", "USER_TO_BUSINESS")]), "status_code": 200},
    ]

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(REIMBURSEMENTS_URL, responses)
        output = read_stream("reimbursements", sync_mode=SyncMode.incremental)

    assert sorted(record_ids(output)) == ["rb-1", "rb-2"], f"expected records from both partitions, got {record_ids(output)}"

    data_requests = requests_to(mocker.request_history, REIMBURSEMENTS_PATH)
    assert len(data_requests) == 2, f"expected one request per direction, got {len(data_requests)}"

    all_params = [query_params(request) for request in data_requests]
    assert {params.get("direction") for params in all_params} == {"BUSINESS_TO_USER", "USER_TO_BUSINESS"}
    for params in all_params:
        assert params.get("updated_after") == START_DATE, f"expected the start date as `updated_after`, got {params}"


def test_check_uses_transactions():
    """`check` succeeds off the `transactions` stream."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(TRANSACTIONS_URL, json=_page([_transaction("tx-1", "2024-06-01T00:00:00+00:00")]))
        status = get_source(CONFIG).check(logging.getLogger("test_check_uses_transactions"), CONFIG)

    assert status.status == Status.SUCCEEDED, f"expected a successful check, got {status}"
    assert requests_to(mocker.request_history, TRANSACTIONS_PATH), "check must exercise the transactions stream"
