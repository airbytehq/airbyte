# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v2/security_monitoring/configuration/security_filters")


class TestSecurityFiltersStream(TestCase):
    @HttpMocker()
    def test_reads_every_security_filter_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListSecurityFilters` takes no paging parameter and returns every security filter.
        request = _request().build()
        security_filters = [
            {"id": "builtin", "type": "security_filters", "attributes": {"name": "Built-in", "is_builtin": True, "version": 3}},
            {"id": "custom", "type": "security_filters", "attributes": {"name": "Custom", "is_builtin": False, "query": "service:web"}},
        ]
        http_mocker.get(
            request,
            DatadogPaginatedResponseBuilder("data").with_records(security_filters).with_meta({"warning": "A filter is disabled."}).build(),
        )

        output = read_stream("security_filters")

        assert output.errors == []
        assert [message.record.data for message in output.records] == security_filters
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert [stream.source_defined_primary_key for stream in catalog.streams if stream.name == "security_filters"] == [[["id"]]]

    @HttpMocker()
    def test_missing_permission_names_security_monitoring_filters_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("security_filters", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "security_filters")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the security_monitoring_filters_read permission: Forbidden, Failed permission authorization "
                "checks. Grant security_monitoring_filters_read to the Application Key in Datadog.",
            )
        ]
