# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.models import FailureType
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import read_stream, stream_errors
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


class TestSyntheticTestsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        full_page = [{"public_id": f"test-{number}"} for number in range(100)]
        last_page = [{"public_id": "test-100"}]
        http_mocker.get(
            DatadogRequestBuilder.synthetic_tests_endpoint().with_query_param("page_size", 100).with_query_param("page_number", 0).build(),
            DatadogPaginatedResponseBuilder("tests").with_records(full_page).build(),
        )
        http_mocker.get(
            DatadogRequestBuilder.synthetic_tests_endpoint().with_query_param("page_size", 100).with_query_param("page_number", 1).build(),
            DatadogPaginatedResponseBuilder("tests").with_records(last_page).build(),
        )

        output = read_stream("synthetic_tests")

        assert output.errors == []
        assert [message.record.data["public_id"] for message in output.records] == [record["public_id"] for record in full_page + last_page]

    @HttpMocker()
    def test_fails_when_synthetic_monitoring_is_not_active(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            DatadogRequestBuilder.synthetic_tests_endpoint().with_query_param("page_size", 100).with_query_param("page_number", 0).build(),
            datadog_error(404, ["Not found"]),
        )

        output = read_stream("synthetic_tests", expecting_error=True)

        errors = stream_errors(output, "synthetic_tests")
        assert [(error.failure_type, error.message) for error in errors] == [
            (
                FailureType.config_error,
                "Synthetic Monitoring is not active for this Datadog account. "
                "Deselect the synthetic_tests stream or activate Synthetic Monitoring in Datadog.",
            )
        ]
