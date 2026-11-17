# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from typing import Any
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v2/integration/opsgenie/accounts")


def _account(account_id: str) -> dict[str, Any]:
    return {"id": account_id, "type": "opsgenie-account", "attributes": {"region": "us"}}


class TestOpsgenieAccountsStream(TestCase):
    @HttpMocker()
    def test_reads_the_whole_list_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListOpsgenieAccounts` takes no paging parameter.
        accounts = [_account("00000000-0000-0000-0000-000000000001"), _account("00000000-0000-0000-0000-000000000002")]
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records(accounts).build())

        output = read_stream("opsgenie_accounts")

        assert output.errors == []
        assert [message.record.data for message in output.records] == accounts
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_removes_the_api_key(self, http_mocker: HttpMocker) -> None:
        # The key is sent when the account is created. The list is not documented to return it, and must never emit it.
        account = _account("00000000-0000-0000-0000-000000000001")
        account["attributes"]["api_key"] = "fake-opsgenie-api-key"
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("data").with_records([account]).build())

        output = read_stream("opsgenie_accounts")

        records = [message.record.data for message in output.records]
        assert output.errors == []
        assert records == [_account("00000000-0000-0000-0000-000000000001")]
        assert "fake-opsgenie-api-key" not in json.dumps(records)

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        stream = next(stream for stream in catalog.streams if stream.name == "opsgenie_accounts")
        assert stream.source_defined_primary_key == [["id"]]

    @HttpMocker()
    def test_missing_permission_names_integrations_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().with_any_query_params().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"])
        )

        output = read_stream("opsgenie_accounts", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "opsgenie_accounts")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the integrations_read permission: Forbidden, Failed permission authorization checks. "
                "Grant integrations_read to the Application Key in Datadog.",
            )
        ]
