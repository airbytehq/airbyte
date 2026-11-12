# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import read_stream
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder


class TestDashboardsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        full_page = [{"id": f"dashboard-{number}"} for number in range(100)]
        last_page = [{"id": "dashboard-100"}]
        http_mocker.get(
            DatadogRequestBuilder.dashboards_endpoint().with_query_param("count", 100).build(),
            DatadogPaginatedResponseBuilder("dashboards").with_records(full_page).build(),
        )
        http_mocker.get(
            DatadogRequestBuilder.dashboards_endpoint().with_query_param("count", 100).with_query_param("start", 100).build(),
            DatadogPaginatedResponseBuilder("dashboards").with_records(last_page).build(),
        )

        output = read_stream("dashboards")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [record["id"] for record in full_page + last_page]
