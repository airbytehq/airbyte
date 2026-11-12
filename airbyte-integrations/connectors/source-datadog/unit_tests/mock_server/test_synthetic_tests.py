# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import read_stream
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder


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
