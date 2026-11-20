# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import read_stream
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder


class TestIncidentsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        full_page = [{"id": f"incident-{number}"} for number in range(100)]
        last_page = [{"id": "incident-100"}]
        first_request = DatadogRequestBuilder.incidents_endpoint().with_query_param("page[size]", 100).build()
        second_request = (
            DatadogRequestBuilder.incidents_endpoint().with_query_param("page[size]", 100).with_query_param("page[offset]", 100).build()
        )
        http_mocker.get(
            first_request,
            DatadogPaginatedResponseBuilder("data")
            .with_records(full_page)
            .with_meta({"pagination": {"offset": 0, "next_offset": 100, "size": 100}})
            .build(),
        )
        http_mocker.get(
            second_request,
            DatadogPaginatedResponseBuilder("data")
            .with_records(last_page)
            .with_meta({"pagination": {"offset": 100, "next_offset": 101, "size": 1}})
            .build(),
        )

        output = read_stream("incidents")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [record["id"] for record in full_page + last_page]
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)

    @HttpMocker()
    def test_ends_after_a_short_page_that_carries_a_next_offset(self, http_mocker: HttpMocker) -> None:
        # The API answers `next_offset` as the offset plus the records returned, so it does not say that more is left.
        request = DatadogRequestBuilder.incidents_endpoint().with_query_param("page[size]", 100).build()
        http_mocker.get(
            request,
            DatadogPaginatedResponseBuilder("data")
            .with_records([{"id": "incident-1"}, {"id": "incident-2"}])
            .with_meta({"pagination": {"offset": 0, "next_offset": 2, "size": 2}})
            .build(),
        )

        output = read_stream("incidents")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["incident-1", "incident-2"]
        http_mocker.assert_number_of_calls(request, 1)
