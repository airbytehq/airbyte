# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import read_stream
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder


def _request(deleted: str) -> DatadogRequestBuilder:
    return DatadogRequestBuilder.service_level_objectives_endpoint().with_query_param("limit", 1000).with_query_param("is_deleted", deleted)


class TestServiceLevelObjectivesStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        full_page = [{"id": f"slo-{number}"} for number in range(1000)]
        last_page = [{"id": "slo-1000"}]
        http_mocker.get(_request("false").build(), DatadogPaginatedResponseBuilder("data").with_records(full_page).build())
        http_mocker.get(
            _request("false").with_query_param("offset", 1000).build(),
            DatadogPaginatedResponseBuilder("data").with_records(last_page).build(),
        )
        http_mocker.get(_request("true").build(), DatadogPaginatedResponseBuilder("data").build())

        output = read_stream("service_level_objectives")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [record["id"] for record in full_page + last_page]

    @HttpMocker()
    def test_reads_active_and_deleted_slos_and_flags_them(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request("false").build(), DatadogPaginatedResponseBuilder("data").with_records([{"id": "active"}]).build())
        http_mocker.get(_request("true").build(), DatadogPaginatedResponseBuilder("data").with_records([{"id": "deleted"}]).build())

        output = read_stream("service_level_objectives")

        records = {message.record.data["id"]: message.record.data for message in output.records}
        assert output.errors == []
        assert len(output.records) == 2
        assert records["active"]["deleted"] is False
        assert records["deleted"]["deleted"] is True
