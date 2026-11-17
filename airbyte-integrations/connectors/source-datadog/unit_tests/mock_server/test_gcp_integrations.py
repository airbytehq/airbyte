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
    return DatadogRequestBuilder("v2/integration/gcp/accounts")


def _service_account(account_id: str) -> dict[str, Any]:
    return {
        "id": account_id,
        "type": "gcp_service_account",
        "attributes": {
            "account_tags": ["env:prod"],
            "automute": True,
            "client_email": "service-account@test-project.iam.gserviceaccount.com",
            "is_cspm_enabled": True,
            "metric_namespace_configs": [{"disabled": False, "filters": ["snapshot.*"], "id": "pubsub"}],
            "monitored_resource_configs": [{"filters": ["env:prod"], "type": "gce_instance"}],
            "region_filter_configs": ["us-east1"],
            "resource_collection_enabled": True,
        },
        "meta": {"accessible_projects": ["test-project"]},
    }


class TestGcpIntegrationsStream(TestCase):
    @HttpMocker()
    def test_reads_the_whole_list_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListGCPSTSAccounts` takes no paging parameter.
        service_accounts = [_service_account("abc-123"), _service_account("def-456")]
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records(service_accounts).build())

        output = read_stream("gcp_integrations")

        assert output.errors == []
        assert [message.record.data for message in output.records] == service_accounts
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        stream = next(stream for stream in catalog.streams if stream.name == "gcp_integrations")
        assert stream.source_defined_primary_key == [["id"]]

    @HttpMocker()
    def test_missing_permission_names_gcp_configuration_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().with_any_query_params().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"])
        )

        output = read_stream("gcp_integrations", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "gcp_integrations")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the gcp_configuration_read permission: Forbidden, Failed permission authorization checks. "
                "Grant gcp_configuration_read to the Application Key in Datadog.",
            )
        ]
