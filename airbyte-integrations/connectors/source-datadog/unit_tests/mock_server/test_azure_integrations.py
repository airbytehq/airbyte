# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from typing import Any
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v1/integration/azure")


def _integration(tenant_name: str, client_id: str) -> dict[str, Any]:
    return {
        "app_service_plan_filters": "",
        "automute": False,
        "client_id": client_id,
        "container_app_filters": "",
        "cspm_enabled": False,
        "custom_metrics_enabled": False,
        "errors": [],
        "host_filters": "key:value,filter:example",
        "metrics_enabled": True,
        "metrics_enabled_default": True,
        "resource_collection_enabled": True,
        "resource_provider_configs": [{"metrics_enabled": False, "namespace": "Microsoft.Compute"}],
        "secretless_auth_enabled": False,
        "tenant_name": tenant_name,
        "usage_metrics_enabled": True,
    }


class TestAzureIntegrationsStream(TestCase):
    @HttpMocker()
    def test_reads_the_whole_list_in_one_request(self, http_mocker: HttpMocker) -> None:
        # The v1 list answers with a bare array and takes no paging parameter.
        integrations = [_integration("tenant-1", "client-1"), _integration("tenant-1", "client-2")]
        request = _request().build()
        http_mocker.get(request, HttpResponse(json.dumps(integrations)))

        output = read_stream("azure_integrations")

        assert output.errors == []
        assert [message.record.data for message in output.records] == integrations
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_removes_the_client_secret(self, http_mocker: HttpMocker) -> None:
        integration = {**_integration("tenant-1", "client-1"), "client_secret": "fake-client-secret"}
        http_mocker.get(_request().build(), HttpResponse(json.dumps([integration])))

        output = read_stream("azure_integrations")

        records = [message.record.data for message in output.records]
        assert output.errors == []
        assert records == [_integration("tenant-1", "client-1")]
        assert "fake-client-secret" not in json.dumps(records)

    def test_declares_the_tenant_and_the_client_as_the_primary_key(self) -> None:
        # The v1 record has no ID. Datadog finds an integration to update or delete by `tenant_name` and `client_id`.
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        stream = next(stream for stream in catalog.streams if stream.name == "azure_integrations")
        assert stream.source_defined_primary_key == [["tenant_name"], ["client_id"]]

    @HttpMocker()
    def test_missing_permission_names_azure_configuration_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().with_any_query_params().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"])
        )

        output = read_stream("azure_integrations", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "azure_integrations")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the azure_configuration_read permission: Forbidden, Failed permission authorization checks. "
                "Grant azure_configuration_read to the Application Key in Datadog.",
            )
        ]
