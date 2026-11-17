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
    return DatadogRequestBuilder("v2/integration/aws/accounts")


def _account(config_id: str, auth_config: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": config_id,
        "type": "account",
        "attributes": {
            "account_tags": ["env:prod"],
            "auth_config": auth_config,
            "aws_account_id": "123456789012",
            "aws_partition": "aws",
            "aws_regions": {"include_all": True},
            "created_at": "2026-11-01T10:00:00.000000Z",
            "logs_config": {
                "lambda_forwarder": {
                    "lambdas": ["arn:aws:lambda:us-east-1:123456789012:function:DatadogForwarder"],
                    "log_source_config": {"tag_filters": [{"source": "s3", "tags": ["env:prod"]}]},
                    "sources": ["s3", "elb"],
                }
            },
            "metrics_config": {"enabled": True, "namespace_filters": {"exclude_only": ["AWS/SQS"]}},
            "modified_at": "2026-11-02T10:00:00.000000Z",
            "resources_config": {"extended_collection": True},
            "traces_config": {"xray_services": {"include_only": []}},
        },
    }


class TestAwsIntegrationsStream(TestCase):
    @HttpMocker()
    def test_reads_the_whole_list_in_one_request_with_the_log_forwarding_settings(self, http_mocker: HttpMocker) -> None:
        # `ListAWSAccounts` takes no paging parameter. The v2 account carries what the deprecated v1 AWS logs list returned.
        accounts = [_account("config-1", {"role_name": "DatadogIntegrationRole"}), _account("config-2", {"role_name": "DatadogRole"})]
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records(accounts).build())

        output = read_stream("aws_integrations")

        assert output.errors == []
        assert [message.record.data for message in output.records] == accounts
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_removes_the_access_key_pair_and_the_external_id(self, http_mocker: HttpMocker) -> None:
        key_pair = {"access_key_id": "AKIAFAKEACCESSKEYID", "secret_access_key": "fake-secret-access-key"}
        role = {"role_name": "DatadogIntegrationRole", "external_id": "fake-external-id"}
        http_mocker.get(
            _request().build(),
            DatadogPaginatedResponseBuilder("data").with_records([_account("config-1", key_pair), _account("config-2", role)]).build(),
        )

        output = read_stream("aws_integrations")

        records = [message.record.data for message in output.records]
        assert output.errors == []
        assert [record["attributes"]["auth_config"] for record in records] == [{}, {"role_name": "DatadogIntegrationRole"}]
        assert [record["attributes"]["aws_account_id"] for record in records] == ["123456789012", "123456789012"]
        for value in ("AKIAFAKEACCESSKEYID", "fake-secret-access-key", "fake-external-id"):
            assert value not in json.dumps(records)

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        stream = next(stream for stream in catalog.streams if stream.name == "aws_integrations")
        assert stream.source_defined_primary_key == [["id"]]

    @HttpMocker()
    def test_missing_permission_names_aws_configuration_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().with_any_query_params().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"])
        )

        output = read_stream("aws_integrations", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "aws_integrations")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the aws_configuration_read permission: Forbidden, Failed permission authorization checks. "
                "Grant aws_configuration_read to the Application Key in Datadog.",
            )
        ]
