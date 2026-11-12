# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import read_stream
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder


class TestServiceLevelObjectivesStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        full_page = [{"id": f"slo-{number}"} for number in range(1000)]
        last_page = [{"id": "slo-1000"}]
        http_mocker.get(
            DatadogRequestBuilder.service_level_objectives_endpoint().with_query_param("limit", 1000).build(),
            DatadogPaginatedResponseBuilder("data").with_records(full_page).build(),
        )
        http_mocker.get(
            DatadogRequestBuilder.service_level_objectives_endpoint()
            .with_query_param("limit", 1000)
            .with_query_param("offset", 1000)
            .build(),
            DatadogPaginatedResponseBuilder("data").with_records(last_page).build(),
        )

        output = read_stream("service_level_objectives")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [record["id"] for record in full_page + last_page]
