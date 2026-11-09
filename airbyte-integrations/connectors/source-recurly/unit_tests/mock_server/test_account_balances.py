# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.test.mock_http import HttpMocker

from .contracts import Parent, StreamCase, assert_requests, dated_params, given_parents, read_case, register
from .request_builder import RequestBuilder
from .response_builder import ResponseBuilder


@pytest.mark.parametrize("empty", [False, True], ids=["two_accounts", "empty_parent"])
def test_account_balances(empty: bool) -> None:
    accounts = [] if empty else [{"id": account, "updated_at": "2025-01-02T00:00:00Z"} for account in ("account1", "account2")]
    case = StreamCase("account_balances", "", {}, {}, parents=(Parent("accounts", dated_params(), accounts),))
    expected = []
    requests = []
    with HttpMocker() as http_mocker:
        given_parents(http_mocker, requests, case)
        for index, account in enumerate(accounts):
            record = {
                "object": "account_balance",
                "account": {"id": account["id"], "code": f"customer-{index}"},
                "past_due": index == 1,
                "balances": [
                    {"currency": "USD", "amount": 12.5, "processing_prepayment_amount": 0, "available_credit_amount": 1.5},
                    {"currency": "EUR", "amount": 5, "processing_prepayment_amount": 1, "available_credit_amount": 0},
                ],
            }
            register(
                http_mocker,
                requests,
                RequestBuilder.endpoint(f"accounts/{account['id']}/balance"),
                ResponseBuilder.singleton(record),
            )
            expected.append(dict(record, account_id=account["id"]))
        output = read_case(case)
        records = [message.record.data for message in output.records]
        assert sorted(record["account_id"] for record in records) == [account["id"] for account in accounts]
        assert sorted(records, key=lambda record: record["account_id"]) == expected
        assert_requests(http_mocker, requests, 1 + len(accounts))
