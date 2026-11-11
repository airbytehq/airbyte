# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import patch

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ConfigBuilder
from .contracts import Parent, StreamCase, dated_params, given_parents, read_case
from .request_builder import RequestBuilder
from .response_builder import ResponseBuilder


@pytest.mark.parametrize(
    "status,message",
    [
        (
            401,
            "Recurly rejected the API key (HTTP 401). In Recurly, open "
            "Integrations > API Credentials, copy an active private API key for "
            "this site, and paste it into the API Key field of this source.",
        ),
        (
            403,
            "Recurly denied access (HTTP 403). Use a private API key from the site "
            "you want to sync, and make sure the key is enabled and allowed to "
            "read data in Recurly under Integrations > API Credentials.",
        ),
    ],
)
def test_new_stream_authentication_errors(status: int, message: str) -> None:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream("gift_cards", SyncMode.full_refresh).build()
    source = get_source(config, catalog=catalog)
    request = RequestBuilder.endpoint("gift_cards").build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            HttpResponse(json.dumps({"error": {"type": "invalid_api_key", "message": "Access denied"}}), status_code=status),
        )
        output = read(source, config=config, catalog=catalog)
        assert not output.records
        assert any(
            error.trace.error.failure_type.value == "config_error" and error.trace.error.message == message for error in output.errors
        )
        http_mocker.assert_number_of_calls(request, 1)
        assert http_mocker._mocker.call_count == 1


def test_account_balances_retries_rate_limits_with_factor_five() -> None:
    case = StreamCase(
        "account_balances",
        "accounts/account1/balance",
        {},
        {},
        parents=(Parent("accounts", dated_params(), [{"id": "account1"}]),),
    )
    record = {"object": "account_balance", "balances": [{"currency": "USD", "amount": 12.5}]}
    request = RequestBuilder.endpoint(case.path).build()
    rate_limited = HttpResponse(
        json.dumps({"error": {"type": "rate_limited", "message": "API rate limit exceeded"}}),
        status_code=429,
        headers={"X-RateLimit-Limit": "5000", "X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1735862700"},
    )
    with HttpMocker() as http_mocker, patch("time.sleep") as sleep:
        parents = []
        given_parents(http_mocker, parents, case)
        http_mocker.get(request, [rate_limited, ResponseBuilder.singleton(record)])
        output = read_case(case)
        assert [message.record.data for message in output.records] == [dict(record, account_id="account1")]
        http_mocker.assert_number_of_calls(parents[0], 1)
        http_mocker.assert_number_of_calls(request, 2)
        assert http_mocker._mocker.call_count == 3
    waits = [call.args[0] for call in sleep.call_args_list if call.args and call.args[0]]
    assert waits == [11.0]
