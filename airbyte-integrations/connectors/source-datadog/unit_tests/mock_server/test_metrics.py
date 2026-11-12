# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import read_stream
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder.metrics_endpoint().with_query_param("window[seconds]", 5184000).with_query_param("page[size]", 10000)


class TestMetricsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages_of_the_60_day_window(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().build(),
            DatadogPaginatedResponseBuilder("data")
            .with_records([{"id": "metric.one"}, {"id": "metric.two"}])
            .with_meta({"pagination": {"next_cursor": "next-page"}})
            .build(),
        )
        http_mocker.get(
            _request().with_query_param("page[cursor]", "next-page").build(),
            DatadogPaginatedResponseBuilder("data")
            .with_records([{"id": "metric.three"}])
            .with_meta({"pagination": {"next_cursor": None}})
            .build(),
        )

        output = read_stream("metrics")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["metric.one", "metric.two", "metric.three"]

    @HttpMocker()
    def test_ends_on_a_null_meta_and_on_a_null_pagination(self, http_mocker: HttpMocker) -> None:
        request = _request().build()
        http_mocker.get(
            request,
            [
                DatadogPaginatedResponseBuilder("data").with_records([{"id": "metric.one"}]).with_meta(None).build(),
                DatadogPaginatedResponseBuilder("data").with_records([{"id": "metric.two"}]).with_meta({"pagination": None}).build(),
            ],
        )

        null_meta = read_stream("metrics")
        null_pagination = read_stream("metrics")

        assert null_meta.errors == []
        assert null_pagination.errors == []
        assert [message.record.data["id"] for message in null_meta.records + null_pagination.records] == ["metric.one", "metric.two"]
        http_mocker.assert_number_of_calls(request, 2)

    @HttpMocker()
    def test_ends_on_an_empty_page(self, http_mocker: HttpMocker) -> None:
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_meta({"pagination": {"next_cursor": "next-page"}}).build())

        output = read_stream("metrics")

        assert output.errors == []
        assert output.records == []
        http_mocker.assert_number_of_calls(request, 1)
