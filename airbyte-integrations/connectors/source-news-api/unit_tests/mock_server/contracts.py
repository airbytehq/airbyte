# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import FailureType, Level, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import get_source
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.request_builder import build_request
from unit_tests.mock_server.response_builder import article_response, error_response


def read_stream(stream: str) -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog)


def assert_config_error(output: EntrypointOutput, expected: str) -> None:
    errors = [message.trace.error for message in output.errors if message.trace.error and expected in message.trace.error.message]
    assert len(errors) == 1, output.errors
    assert errors[0].failure_type == FailureType.config_error
    assert errors[0].message == expected


class StreamContracts:
    stream: str

    @pytest.mark.parametrize("first_count,second_count", [(0, None), (1, None), (100, 1), (100, 0)])
    def test_read_records_and_pagination(self, first_count: int, second_count: int | None) -> None:
        with HttpMocker() as mocker:
            first = build_request(self.stream)
            mocker.get(first, article_response(0, first_count))
            if second_count is not None:
                second = build_request(self.stream, 2)
                mocker.get(second, article_response(first_count, second_count))
            output = read_stream(self.stream)
            mocker.assert_number_of_calls(first, 1)
            if second_count is not None:
                mocker.assert_number_of_calls(second, 1)
        count = first_count + (second_count or 0)
        assert len(output.records) == count
        assert [record.record.data["url"] for record in output.records] == [
            f"https://example.com/articles/{index}" for index in range(count)
        ]
        assert output.errors == []

    @pytest.mark.parametrize("earlier_page", [False, True])
    def test_maximum_results_is_ignored(self, earlier_page: bool) -> None:
        with HttpMocker() as mocker:
            if earlier_page:
                first = build_request(self.stream)
                mocker.get(first, article_response(0, 100))
            failed = build_request(self.stream, 2 if earlier_page else 1)
            mocker.get(failed, error_response(426, "maximumResultsReached", "Too many results."))
            output = read_stream(self.stream)
            mocker.assert_number_of_calls(failed, 1)
            if earlier_page:
                mocker.assert_number_of_calls(first, 1)
        count = 100 if earlier_page else 0
        assert len(output.records) == count
        assert [record.record.data["url"] for record in output.records] == [
            f"https://example.com/articles/{index}" for index in range(count)
        ]
        assert output.errors == []
        assert not any(log.log.level == Level.ERROR for log in output.logs)

    @pytest.mark.parametrize(
        "status,code,message",
        [
            (400, "parametersMissing", "Required parameters are missing."),
            (426, "upgradeRequired", "Your plan does not include this endpoint."),
        ],
    )
    def test_config_errors(self, status: int, code: str, message: str) -> None:
        with HttpMocker() as mocker:
            request = build_request(self.stream)
            mocker.get(request, error_response(status, code, message))
            output = read_stream(self.stream)
            mocker.assert_number_of_calls(request, 1)
        expected = f"News API rejected the `{self.stream}` request: {message}"
        if self.stream == "everything" and code == "parametersMissing":
            expected += (
                " This stream requires at least one of `search_query`, `sources` or `domains` to be set in the source"
                " configuration; set one of them or deselect the stream."
            )
        assert output.records == []
        assert_config_error(output, expected)
