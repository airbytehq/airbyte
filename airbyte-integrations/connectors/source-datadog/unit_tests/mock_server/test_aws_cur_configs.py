# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from typing import Any
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v2/cost/aws_cur_config")


def _config(config_id: str) -> dict[str, Any]:
    return {
        "id": config_id,
        "type": "aws_cur_config",
        "attributes": {
            "account_filters": {"excluded_accounts": [], "include_new_accounts": True, "included_accounts": []},
            "account_id": "123456789123",
            "bucket_name": "dd-cost-bucket",
            "bucket_region": "us-east-1",
            "created_at": "2023-01-01T12:00:00.000000",
            "error_messages": [],
            "months": 36,
            "report_name": "dd-report-name",
            "report_prefix": "dd-report-prefix",
            "status": "active",
            "status_updated_at": "2023-01-01T12:00:00.000000",
            "updated_at": "2023-01-01T12:00:00.000000",
        },
    }


class TestAwsCurConfigsStream(TestCase):
    @HttpMocker()
    def test_reads_the_whole_list_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListCostAWSCURConfigs` takes no paging parameter.
        configs = [_config("123"), _config("456")]
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records(configs).build())

        output = read_stream("aws_cur_configs")

        assert output.errors == []
        assert [message.record.data for message in output.records] == configs
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        stream = next(stream for stream in catalog.streams if stream.name == "aws_cur_configs")
        assert stream.source_defined_primary_key == [["id"]]

    @HttpMocker()
    def test_missing_permission_names_cloud_cost_management_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().with_any_query_params().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"])
        )

        output = read_stream("aws_cur_configs", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "aws_cur_configs")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the cloud_cost_management_read permission: Forbidden, Failed permission authorization checks. "
                "Grant cloud_cost_management_read to the Application Key in Datadog.",
            )
        ]
