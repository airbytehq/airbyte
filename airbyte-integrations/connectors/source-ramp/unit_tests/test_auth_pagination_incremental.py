# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-ramp` covering the manifest behaviours that are easy to regress:

- the `SessionTokenAuthenticator` login call (HTTP Basic client credentials, form body with the
  read scopes) and the `Bearer` token it hands to the data requests
- `DefaultPaginator` + `CursorPagination`: `page_size` on every request, `start` set to the `id`
  of the previous page's last record, and a null-safe stop condition
- `transactions` incremental sync is filtered server-side via `updated_after` and always requests
  `state=ALL` so declined transactions are emitted
- `reimbursements` incremental sync is filtered server-side via `updated_after`, once per
  `direction` partition
- Ramp auth and scope errors are surfaced as `config_error` with actionable messages
- `api_budget` throttles requests under Ramp's 200 requests / 10 s limit
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


def _ramp_error(error_code: str, message: str) -> dict:
    """Ramp's `DeveloperApiErrorResponse` body."""
    return {"error_v2": {"error_code": error_code, "message": message, "error_id": "abc123", "notes": "", "additional_info": {}}}


def _config_errors(output) -> list:
    return [
        t.trace.error for t in output.trace_messages if t.trace.error is not None and t.trace.error.failure_type == FailureType.config_error
    ]


def test_token_request():
    """Reading a stream logs in once with HTTP Basic client credentials and then sends `Bearer <token>`."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(CARDS_URL, json=_page([_card("card-1")]))
        output = read_stream("cards")

    assert record_ids(output) == ["card-1"]

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

    data_requests = requests_to(mocker.request_history, CARDS_PATH)
    assert len(data_requests) == 1
    assert data_requests[0].headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"


def test_pagination():
    """`start` carries the `id` of the previous page's last record and `page_size` is sent on every page."""
    page_1 = _page([_card("card-1"), _card("card-2")], next_url=f"{CARDS_URL}?start=card-2")
    page_2 = _page([_card("card-3"), _card("card-4")])

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(CARDS_URL, [{"json": page_1, "status_code": 200}, {"json": page_2, "status_code": 200}])
        output = read_stream("cards")

    assert record_ids(output) == ["card-1", "card-2", "card-3", "card-4"]

    data_requests = requests_to(mocker.request_history, CARDS_PATH)
    assert len(data_requests) == 2, f"expected 2 paginated requests, got {len(data_requests)}"

    first_params = query_params(data_requests[0])
    assert first_params.get("page_size") == "50"
    assert "start" not in first_params, f"first request must not carry a page token, got {first_params}"

    second_params = query_params(data_requests[1])
    assert second_params.get("start") == "card-2", f"second request must resume from the last record id, got {second_params}"
    assert second_params.get("page_size") == "50"


def test_pagination_stops_on_null_page():
    """A response whose `page` key is present but null must end the read instead of looping."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(
            CARDS_URL,
            [
                {"json": {"data": [_card("card-1")], "page": None}, "status_code": 200},
                # A stop condition that is not null-safe loops on the same page forever. Failing the
                # second request keeps that regression a fast test failure instead of a hung suite.
                {"json": {}, "status_code": 400},
            ],
        )
        output = read_stream("cards")

    assert record_ids(output) == ["card-1"]
    data_requests = requests_to(mocker.request_history, CARDS_PATH)
    assert len(data_requests) == 1, f"expected the read to stop after one page, got {len(data_requests)} requests"


def test_transactions_server_side_incremental_and_state_all():
    """`transactions` sends the state cursor as `updated_after` and asks for `state=ALL` so declined records are emitted."""
    cursor = "2024-06-01T00:00:00Z"
    state = StateBuilder().with_stream_state("transactions", {"updated_at": cursor}).build()
    declined = dict(_transaction("tx-declined", "2024-07-02T00:00:00+00:00"), state="DECLINED")
    response = _page([_transaction("tx-new", "2024-07-01T00:00:00+00:00"), declined])

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(TRANSACTIONS_URL, json=response)
        output = read_stream("transactions", sync_mode=SyncMode.incremental, state=state)

    assert record_ids(output) == ["tx-new", "tx-declined"], f"expected every record the API returned, got {record_ids(output)}"

    data_requests = requests_to(mocker.request_history, TRANSACTIONS_PATH)
    assert len(data_requests) == 1, f"expected a single request against /transactions, got {len(data_requests)}"
    params = query_params(data_requests[0])
    assert params.get("updated_after") == cursor, f"transactions must filter server-side with the state cursor, got {params}"
    assert params.get("state") == "ALL", f"transactions must request state=ALL to include declined transactions, got {params}"


def test_transactions_first_sync_uses_default_start_date():
    """Without `start_date` in the config, the first sync starts from the spec default."""
    config = {key: value for key, value in CONFIG.items() if key != "start_date"}

    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(TRANSACTIONS_URL, json=_page([_transaction("tx-1", "2024-06-01T00:00:00+00:00")]))
        output = read_stream("transactions", config=config, sync_mode=SyncMode.incremental)

    assert record_ids(output) == ["tx-1"]
    params = query_params(requests_to(mocker.request_history, TRANSACTIONS_PATH)[0])
    assert params.get("updated_after") == "2019-01-01T00:00:00Z", f"expected the default start date as `updated_after`, got {params}"


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


@pytest.mark.parametrize(
    "status_code, body, expected_fragment",
    [
        pytest.param(
            400, _ramp_error("5006", "client_id is malformed, invalid length."), "client_id is malformed", id="malformed-client-id"
        ),
        pytest.param(
            401, _ramp_error("5001", "Client credentials not found or malformed."), "Client credentials not found", id="wrong-secret"
        ),
    ],
)
def test_login_errors_are_config_errors(status_code, body, expected_fragment):
    """Token endpoint rejections surface as `config_error` naming Ramp's message, without retrying."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, status_code=status_code, json=body)
        mocker.get(TRANSACTIONS_URL, json=_page([]))
        output = read_stream("transactions")

    errors = _config_errors(output)
    assert errors, f"expected a config_error trace, got {[t.trace.error for t in output.trace_messages if t.trace.error]}"
    assert expected_fragment in errors[0].message
    assert "Ramp > Company > Developer" in errors[0].message
    assert len(requests_to(mocker.request_history, TOKEN_PATH)) == 1, "credential errors must not be retried"


@pytest.mark.parametrize(
    "status_code, body, expected_fragment",
    [
        pytest.param(
            403, _ramp_error("DEVELOPER_7100", "These scopes are not allowed for this token: cards:read"), "cards:read", id="missing-scope"
        ),
        pytest.param(
            404, _ramp_error("DEVELOPER_7002", "Access token with given access_token not found"), "access token", id="revoked-token-404"
        ),
        pytest.param(
            401, _ramp_error("DEVELOPER_7002", "Access token with given access_token not found"), "access token", id="revoked-token-401"
        ),
        pytest.param(401, {"error": {"message": "Unauthorized"}}, "credentials", id="generic-401"),
    ],
)
def test_data_request_auth_errors_are_config_errors(status_code, body, expected_fragment):
    """Scope and token errors on data requests surface as `config_error` with an actionable message."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(CARDS_URL, status_code=status_code, json=body)
        output = read_stream("cards")

    errors = _config_errors(output)
    assert errors, f"expected a config_error trace, got {[t.trace.error for t in output.trace_messages if t.trace.error]}"
    assert expected_fragment in errors[0].message
    assert len(requests_to(mocker.request_history, CARDS_PATH)) == 1, "auth errors must not be retried"


def test_unmatched_404_keeps_default_message():
    """A 404 without Ramp's `DEVELOPER_7002` code keeps the CDK default handling instead of the token message."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(CARDS_URL, status_code=404, json={"error": {"message": "not found"}})
        output = read_stream("cards")

    messages = [t.trace.error.message for t in output.trace_messages if t.trace.error is not None]
    assert messages, "expected the failed read to be reported"
    assert all("access token" not in message for message in messages), messages


def test_api_budget_matches_ramp_rate_limit():
    """The manifest declares a moving-window budget under Ramp's 200 requests per 10 s."""
    budget = get_source(CONFIG).resolved_manifest["api_budget"]
    assert budget["type"] == "HTTPAPIBudget"
    (policy,) = budget["policies"]
    (rate,) = policy["rates"]
    assert policy["type"] == "MovingWindowCallRatePolicy"
    assert rate["interval"] == "PT10S"
    assert 0 < rate["limit"] <= 200


def test_spec_start_date_optional_with_default():
    """`start_date` is optional, defaults, and accepts fractional seconds; `api_url` must be https."""
    import re

    spec = get_source(CONFIG).spec(logging.getLogger("spec")).connectionSpecification
    assert "start_date" not in spec["required"]
    start_date = spec["properties"]["start_date"]
    assert start_date["default"] == "2019-01-01T00:00:00Z"
    assert re.match(start_date["pattern"], "2024-01-01T00:00:00.123Z")
    assert re.match(start_date["pattern"], "2024-01-01T00:00:00Z")
    assert not re.match(spec["properties"]["api_url"]["pattern"], "http://demo-api.ramp.com")
    assert "transactions:read" in spec["properties"]["client_id"]["description"]


def test_check_uses_transactions():
    """`check` succeeds off the `transactions` stream."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(TRANSACTIONS_URL, json=_page([_transaction("tx-1", "2024-06-01T00:00:00+00:00")]))
        status = get_source(CONFIG).check(logging.getLogger("test_check_uses_transactions"), CONFIG)

    assert status.status == Status.SUCCEEDED, f"expected a successful check, got {status}"
    assert requests_to(mocker.request_history, TRANSACTIONS_PATH), "check must exercise the transactions stream"
