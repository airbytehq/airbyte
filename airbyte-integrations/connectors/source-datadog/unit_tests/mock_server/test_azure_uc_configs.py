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
    return DatadogRequestBuilder("v2/cost/azure_uc_config")


def _config_pair(account_id: str) -> dict[str, Any]:
    configs = [
        {
            "account_id": "1234abcd-1234-abcd-1234-1234abcd1234",
            "client_id": "1234abcd-1234-abcd-1234-1234abcd1234",
            "created_at": "2023-01-01T12:00:00.000000",
            "dataset_type": dataset_type,
            "error_messages": [],
            "export_name": f"dd-{dataset_type}-export",
            "export_path": "dd-export-path",
            "id": f"{account_id}-{dataset_type}",
            "months": 36,
            "scope": "/subscriptions/1234abcd-1234-abcd-1234-1234abcd1234",
            "status": "active",
            "status_updated_at": "2023-01-01T12:00:00.000000",
            "storage_account": "dd-storage-account",
            "storage_container": "dd-storage-container",
            "updated_at": "2023-01-01T12:00:00.000000",
        }
        for dataset_type in ("actual", "amortized")
    ]
    return {"id": account_id, "type": "azure_uc_configs", "attributes": {"configs": configs, "id": f"{account_id}-pair"}}


class TestAzureUcConfigsStream(TestCase):
    @HttpMocker()
    def test_reads_the_whole_list_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListCostAzureUCConfigs` takes no paging parameter. One record holds the configs of one account.
        pairs = [_config_pair("123456789123"), _config_pair("987654321987")]
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records(pairs).build())

        output = read_stream("azure_uc_configs")

        assert output.errors == []
        assert [message.record.data for message in output.records] == pairs
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        stream = next(stream for stream in catalog.streams if stream.name == "azure_uc_configs")
        assert stream.source_defined_primary_key == [["id"]]

    @HttpMocker()
    def test_missing_permission_names_cloud_cost_management_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().with_any_query_params().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"])
        )

        output = read_stream("azure_uc_configs", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "azure_uc_configs")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the cloud_cost_management_read permission: Forbidden, Failed permission authorization checks. "
                "Grant cloud_cost_management_read to the Application Key in Datadog.",
            )
        ]
