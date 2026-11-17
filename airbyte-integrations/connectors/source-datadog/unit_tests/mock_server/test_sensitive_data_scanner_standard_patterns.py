# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import CONFIG, get_source, read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder("v2/sensitive-data-scanner/config/standard-patterns")


class TestSensitiveDataScannerStandardPatternsStream(TestCase):
    @HttpMocker()
    def test_reads_every_standard_pattern_in_one_request(self, http_mocker: HttpMocker) -> None:
        # `ListStandardPatterns` takes no paging parameter and returns the whole library.
        request = _request().build()
        patterns = [
            {
                "id": "pattern-1",
                "type": "sensitive_data_scanner_standard_pattern",
                "attributes": {"name": "Credit Card Number", "priority": 1, "included_keywords": ["credit card"]},
            },
            {"id": "pattern-2", "type": "sensitive_data_scanner_standard_pattern", "attributes": {"name": "Email Address", "priority": 3}},
        ]
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_records(patterns).build())

        output = read_stream("sensitive_data_scanner_standard_patterns")

        assert output.errors == []
        assert [message.record.data for message in output.records] == patterns
        http_mocker.assert_number_of_calls(request, 1)

    def test_declares_id_as_the_primary_key(self) -> None:
        catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

        assert [
            stream.source_defined_primary_key for stream in catalog.streams if stream.name == "sensitive_data_scanner_standard_patterns"
        ] == [[["id"]]]

    @HttpMocker()
    def test_missing_permission_names_data_scanner_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream("sensitive_data_scanner_standard_patterns", expecting_error=True)

        assert [(error.failure_type, error.message) for error in stream_errors(output, "sensitive_data_scanner_standard_patterns")] == [
            (
                FailureType.config_error,
                "The Application Key lacks the data_scanner_read permission: Forbidden, Failed permission authorization checks. "
                "Grant data_scanner_read to the Application Key in Datadog.",
            )
        ]
