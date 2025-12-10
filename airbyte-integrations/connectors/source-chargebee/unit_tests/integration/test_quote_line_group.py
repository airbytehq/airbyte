# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import RequestBuilder
from .response_builder import (
    empty_response,
    quote_line_group_response,
    quote_response,
    quote_response_multiple,
)
from .utils import config, read_output


_STREAM_NAME = "quote_line_group"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestQuoteLineGroupStream(TestCase):
    """Tests for the quote_line_group stream (substream of quote)."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for quote_line_group stream (substream of quote)."""
        http_mocker.get(
            RequestBuilder.quotes_endpoint().with_any_query_params().build(),
            quote_response(),
        )
        http_mocker.get(
            RequestBuilder.quote_line_groups_endpoint("quote_001").with_any_query_params().build(),
            quote_line_group_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) >= 1
        assert output.records[0].record.data["id"] == "qlg_001"

    @HttpMocker()
    def test_with_multiple_parents(self, http_mocker: HttpMocker) -> None:
        """Test quote_line_group substream with multiple parent quotes."""
        http_mocker.get(
            RequestBuilder.quotes_endpoint().with_any_query_params().build(),
            quote_response_multiple(),
        )
        http_mocker.get(
            RequestBuilder.quote_line_groups_endpoint("quote_001").with_any_query_params().build(),
            quote_line_group_response(),
        )
        http_mocker.get(
            RequestBuilder.quote_line_groups_endpoint("quote_002").with_any_query_params().build(),
            quote_line_group_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) >= 2

    @HttpMocker()
    def test_error_404_ignored(self, http_mocker: HttpMocker) -> None:
        """Test that 404 errors are ignored for quote_line_group (IGNORE action)."""
        from http import HTTPStatus

        from .response_builder import error_response

        http_mocker.get(
            RequestBuilder.quotes_endpoint().with_any_query_params().build(),
            quote_response(),
        )
        http_mocker.get(
            RequestBuilder.quote_line_groups_endpoint("quote_001").with_any_query_params().build(),
            error_response(HTTPStatus.NOT_FOUND),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 0
