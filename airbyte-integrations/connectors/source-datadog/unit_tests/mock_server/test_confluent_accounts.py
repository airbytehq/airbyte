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
    return DatadogRequestBuilder("v2/integrations/confluent-cloud/accounts")


def _account(account_id: str) -> dict[str, Any]:
    return {
        "id": account_id,
        "type": "confluent-cloud-accounts",
        "attributes": {
            "resources": [{"enable_custom_metrics": False, "id": "resource-1", "resource_type": "kafka", "tags": ["env:prod"]}],
            "tags": ["myTag"],
        },
    }


class TestConfluentAccountsStream(TestCase):
    @HttpMocker()
    def test_reads_the_whole_list_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListConfluentAccount` takes no paging parameter.
        accounts = [_account("abc-123"), _account("def-456")]
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records(accounts).build())

        output = read_stream("confluent_accounts")

        assert output.errors == []
        assert [message.record.data for message in output.records] == accounts
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_removes_the_api_key_and_the_api_secret(self, http_mocker: HttpMocker) -> None:
        # The list returns the API key. The secret is sent when the account is created and must never be emitted either.
        account = _account("abc-123")
        account["attributes"].update({"api_key": "fake-confluent-api-key", "api_secret": "fake-confluent-api-secret"})
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("data").with_records([account]).build())

        output = read_stream("confluent_accounts")

        records = [message.record.data for message in output.records]
        assert output.errors == []
        assert records == [_account("abc-123")]
        for value in ("fake-confluent-api-key", "fake-confluent-api-secret"):
            assert value not in json.dumps(records)

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        stream = next(stream for stream in catalog.streams if stream.name == "confluent_accounts")
        assert stream.source_defined_primary_key == [["id"]]

    @HttpMocker()
    def test_missing_permission_names_integrations_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().with_any_query_params().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"])
        )

        output = read_stream("confluent_accounts", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "confluent_accounts")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the integrations_read permission: Forbidden, Failed permission authorization checks. "
                "Grant integrations_read to the Application Key in Datadog.",
            )
        ]
