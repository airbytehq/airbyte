# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any
from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import read_stream
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder


_START_DATE = "2026-10-05T00:00:00Z"
_END_DATE = "2026-10-06T00:00:00Z"
_CONFIG = ConfigBuilder().with_start_date(_START_DATE).with_end_date(_END_DATE).build()


def _request() -> DatadogRequestBuilder:
    return (
        DatadogRequestBuilder.logs_endpoint()
        .with_query_param("filter[from]", _START_DATE)
        .with_query_param("filter[to]", _END_DATE)
        .with_query_param("page[limit]", 5000)
    )


def _log(log_id: str) -> dict[str, Any]:
    return {"id": log_id, "attributes": {"timestamp": "2026-10-05T10:00:00.000Z"}}


class TestLogsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().build(),
            DatadogPaginatedResponseBuilder("data")
            .with_records([_log("log-1"), _log("log-2")])
            .with_meta({"page": {"after": "next-page"}})
            .build(),
        )
        http_mocker.get(
            _request().with_query_param("page[cursor]", "next-page").build(),
            DatadogPaginatedResponseBuilder("data").with_records([_log("log-3")]).build(),
        )

        output = read_stream("logs", config=_CONFIG)

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["log-1", "log-2", "log-3"]

    @HttpMocker()
    def test_ends_on_a_null_meta_and_on_a_null_page(self, http_mocker: HttpMocker) -> None:
        request = _request().build()
        http_mocker.get(
            request,
            [
                DatadogPaginatedResponseBuilder("data").with_records([_log("log-1")]).with_meta(None).build(),
                DatadogPaginatedResponseBuilder("data").with_records([_log("log-2")]).with_meta({"page": None}).build(),
            ],
        )

        null_meta = read_stream("logs", config=_CONFIG)
        null_page = read_stream("logs", config=_CONFIG)

        assert null_meta.errors == []
        assert null_page.errors == []
        assert [message.record.data["id"] for message in null_meta.records + null_page.records] == ["log-1", "log-2"]
        http_mocker.assert_number_of_calls(request, 2)

    @HttpMocker()
    def test_ends_on_an_empty_page(self, http_mocker: HttpMocker) -> None:
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_meta({"page": {"after": "next-page"}}).build())

        output = read_stream("logs", config=_CONFIG)

        assert output.errors == []
        assert output.records == []
        http_mocker.assert_number_of_calls(request, 1)
