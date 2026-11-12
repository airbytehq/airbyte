# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import read_stream
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder.audit_logs_endpoint().with_query_param("page[limit]", 1000)


class TestAuditLogsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().build(),
            DatadogPaginatedResponseBuilder("data")
            .with_records([{"id": "event-1"}, {"id": "event-2"}])
            .with_meta({"page": {"after": "next-page"}})
            .build(),
        )
        http_mocker.get(
            _request().with_query_param("page[cursor]", "next-page").build(),
            DatadogPaginatedResponseBuilder("data").with_records([{"id": "event-3"}]).with_meta({"status": "done"}).build(),
        )

        output = read_stream("audit_logs")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["event-1", "event-2", "event-3"]

    @HttpMocker()
    def test_ends_on_a_null_meta_and_on_a_null_page(self, http_mocker: HttpMocker) -> None:
        request = _request().build()
        http_mocker.get(
            request,
            [
                DatadogPaginatedResponseBuilder("data").with_records([{"id": "event-1"}]).with_meta(None).build(),
                DatadogPaginatedResponseBuilder("data").with_records([{"id": "event-2"}]).with_meta({"page": None}).build(),
            ],
        )

        null_meta = read_stream("audit_logs")
        null_page = read_stream("audit_logs")

        assert null_meta.errors == []
        assert null_page.errors == []
        assert [message.record.data["id"] for message in null_meta.records + null_page.records] == ["event-1", "event-2"]
        http_mocker.assert_number_of_calls(request, 2)

    @HttpMocker()
    def test_ends_on_an_empty_page(self, http_mocker: HttpMocker) -> None:
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_meta({"page": {"after": "next-page"}}).build())

        output = read_stream("audit_logs")

        assert output.errors == []
        assert output.records == []
        http_mocker.assert_number_of_calls(request, 1)
