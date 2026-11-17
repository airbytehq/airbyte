# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v2/apm/config/retention-filters")


class TestApmRetentionFiltersStream(TestCase):
    @HttpMocker()
    def test_reads_every_retention_filter_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListApmRetentionFilters` takes no paging parameter and returns the whole ordered list.
        request = _request().build()
        filters = [
            {"id": "filter-1", "type": "apm_retention_filter", "attributes": {"name": "errors", "rate": 1.0, "execution_order": 1}},
            {"id": "filter-2", "type": "apm_retention_filter", "attributes": {"name": "checkout", "rate": 0.5, "execution_order": 2}},
        ]
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records(filters).build())

        output = read_stream("apm_retention_filters")

        assert output.errors == []
        assert [message.record.data for message in output.records] == filters
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert [stream.source_defined_primary_key for stream in catalog.streams if stream.name == "apm_retention_filters"] == [[["id"]]]

    @HttpMocker()
    def test_missing_permission_names_apm_retention_filter_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("apm_retention_filters", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "apm_retention_filters")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the apm_retention_filter_read permission: Forbidden, Failed permission authorization checks. "
                "Grant apm_retention_filter_read to the Application Key in Datadog.",
            )
        ]
