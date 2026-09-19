# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from typing import Any, Mapping

import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG: Mapping[str, Any] = {
    "tenant_id": "test-tenant",
    "start_date": "2024-01-01T00:00:00Z",
    "credentials": {
        "auth_type": "oauth2_access_token",
        "access_token": "test-token",
    },
}
BASE_URL = "https://api.xero.com/api.xro/2.0/"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def request(path: str) -> HttpRequest:
    return HttpRequest(
        url=f"{BASE_URL}{path}",
        query_params={"page": "1", "pageSize": "1000"},
    )


def response(body: Mapping[str, Any], status_code: int) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def read_stream(stream_name: str, expecting_exception: bool = False):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = get_source(CONFIG, catalog)
    return read(source, CONFIG, catalog, expecting_exception=expecting_exception)


def error_response(message: str, error_number: int = 51, error_type: str = "HighVolumeException") -> HttpResponse:
    return response(
        {
            "ErrorNumber": error_number,
            "Type": error_type,
            "Message": message,
        },
        status_code=400,
    )


def test_check_reads_organisations_not_bank_transactions() -> None:
    with HttpMocker() as http_mocker:
        organisation_request = request("Organisation")
        bank_transaction_request = request("BankTransactions")
        http_mocker.get(
            organisation_request,
            response({"Organisations": [{"OrganisationID": "org-1", "Name": "Test Org"}]}, status_code=200),
        )
        http_mocker.get(
            bank_transaction_request,
            error_response("Your request is not filtering BankTransactions efficiently."),
        )

        status = get_source(CONFIG).check(logging.getLogger("airbyte"), CONFIG)

        assert status.status == Status.SUCCEEDED
        http_mocker.assert_number_of_calls(bank_transaction_request, 0)


def test_check_fails_with_high_volume_message_when_organisations_rejected() -> None:
    message = "Your request is not filtering Organisation efficiently. Please use a narrower filter."
    with HttpMocker() as http_mocker:
        organisation_request = request("Organisation")
        http_mocker.get(organisation_request, error_response(message))

        status = get_source(CONFIG).check(logging.getLogger("airbyte"), CONFIG)

        assert status.status == Status.FAILED
        assert "HighVolumeException" in status.message
        assert "not filtering" in status.message
        assert message in status.message


def test_bank_transactions_high_volume_error_is_config_error() -> None:
    message = "Your request is not filtering BankTransactions efficiently."
    with HttpMocker() as http_mocker:
        bank_transaction_request = request("BankTransactions")
        http_mocker.get(bank_transaction_request, error_response(message))

        output = read_stream("bank_transactions", expecting_exception=True)

        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert message in error.message


def test_generic_400_is_not_treated_as_high_volume() -> None:
    with HttpMocker() as http_mocker:
        bank_transaction_request = request("BankTransactions")
        http_mocker.get(
            bank_transaction_request,
            error_response(
                "A validation exception occurred",
                error_number=10,
                error_type="ValidationException",
            ),
        )

        output = read_stream("bank_transactions", expecting_exception=True)

        assert output.errors
        assert "too many records" not in output.errors[0].trace.error.message
