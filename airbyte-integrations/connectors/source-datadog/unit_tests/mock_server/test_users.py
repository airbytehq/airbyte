# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import read_stream
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder


def _request() -> DatadogRequestBuilder:
    return DatadogRequestBuilder.users_endpoint().with_query_param("page[size]", 100)


class TestUsersStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        full_page = [{"id": f"user-{number}"} for number in range(100)]
        last_page = [{"id": "user-100"}]
        http_mocker.get(_request().build(), DatadogPaginatedResponseBuilder("data").with_records(full_page).build())
        http_mocker.get(
            _request().with_query_param("page[number]", 1).build(),
            DatadogPaginatedResponseBuilder("data").with_records(last_page).build(),
        )

        output = read_stream("users")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [user["id"] for user in full_page + last_page]
