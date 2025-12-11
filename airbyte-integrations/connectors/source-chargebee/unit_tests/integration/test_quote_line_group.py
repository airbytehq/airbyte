# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

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

    @HttpMocker()
    def test_both_transformations(self, http_mocker: HttpMocker) -> None:
        """
        Test that BOTH transformations work together:
        1. AddFields adds quote_id from parent stream slice
        2. CustomFieldTransformation converts cf_* fields to custom_fields array
        """
        # Mock parent quote stream
        http_mocker.get(
            RequestBuilder.quotes_endpoint().with_any_query_params().build(),
            quote_response(),
        )

        # Mock quote_line_group substream (with cf_ fields)
        http_mocker.get(
            RequestBuilder.quote_line_groups_endpoint("quote_001").with_any_query_params().build(),
            quote_line_group_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)

        assert len(output.records) >= 1
        record_data = output.records[0].record.data

        # ========== Test Transformation #1: AddFields ==========
        assert "quote_id" in record_data, "AddFields transformation should add quote_id field"
        assert record_data["quote_id"] == "quote_001", "quote_id should match parent stream's id"

        # ========== Test Transformation #2: CustomFieldTransformation ==========
        assert not any(key.startswith("cf_") for key in record_data.keys()), "cf_ fields should be removed from top level"
        assert "custom_fields" in record_data
        assert isinstance(record_data["custom_fields"], list)
        assert len(record_data["custom_fields"]) == 2

        custom_fields = {cf["name"]: cf["value"] for cf in record_data["custom_fields"]}
        assert len(custom_fields) == 2

    @HttpMocker()
    def test_incremental_sync_with_state_and_params(self, http_mocker: HttpMocker) -> None:
        """
        Test incremental sync with prior state and validate request parameters.

        This test validates:
        1. State from previous sync is accepted
        2. Correct request parameters are sent (sort_by, include_deleted, updated_at[between])
        3. State advances to latest record's cursor value
        """
        # ARRANGE: Previous state from last sync
        previous_state_timestamp = 1704067200  # 2024-01-01T00:00:00
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated_at": previous_state_timestamp}).build()

        # Mock parent quote stream with state params
        http_mocker.get(
            RequestBuilder.quotes_endpoint()
            .with_sort_by_asc("updated_at")
            .with_include_deleted("true")
            .with_updated_at_between(previous_state_timestamp, 1705320000)  # Frozen time: 2024-01-15T12:00:00Z
            .with_limit(100)
            .build(),
            quote_response(),
        )

        # Mock quote_line_group substream
        http_mocker.get(
            RequestBuilder.quote_line_groups_endpoint("quote_001").with_any_query_params().build(),
            quote_line_group_response(),
        )

        # ACT: Run incremental sync with state
        output = read_output(config_builder=config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental, state=state)

        # ASSERT: Records returned
        assert len(output.records) >= 1, "Should return at least 1 record"
        record = output.records[0].record.data

        # ASSERT: Record data is correct
        assert record["id"] == "qlg_001"
        assert record["updated_at"] >= previous_state_timestamp, "Record should be from after the state timestamp"

        # ASSERT: State message emitted
        assert len(output.state_messages) > 0, "Should emit state messages"

        # ASSERT: State advances to latest record
        latest_state = output.state_messages[-1].state.stream.stream_state
        latest_cursor_value = int(latest_state.__dict__["updated_at"])

        # State should advance beyond previous state
        assert latest_cursor_value > previous_state_timestamp, f"State should advance: {latest_cursor_value} > {previous_state_timestamp}"

        # State should match the latest record's cursor value
        assert latest_cursor_value == 1705312800, f"State should be latest record's cursor value: expected 1705312800, got {latest_cursor_value}"
