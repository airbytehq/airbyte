# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .request_builder import RequestBuilder
from .response_builder import configuration_incompatible_response, event_response
from .utils import config, read_output


_STREAM_NAME = "event"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestEventStream(TestCase):
    """Tests for the event stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for event stream."""
        http_mocker.get(
            RequestBuilder.events_endpoint().with_any_query_params().build(),
            event_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "ev_001"

    @HttpMocker()
    def test_incremental_emits_state(self, http_mocker: HttpMocker) -> None:
        """Test that incremental sync emits state message."""
        http_mocker.get(
            RequestBuilder.events_endpoint().with_any_query_params().build(),
            event_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

        # Verify exactly 1 record returned
        assert len(output.records) == 1

        # Verify state message was emitted
        assert len(output.state_messages) > 0

        # Verify state contains correct cursor value (event uses occurred_at)
        latest_state = output.state_messages[-1].state.stream.stream_state
        latest_cursor_value = int(latest_state.__dict__["occurred_at"])

        # Check response file for the actual timestamp value!
        assert latest_cursor_value == 1705312800  # From event.json

    @HttpMocker()
    def test_transformation_custom_fields(self, http_mocker: HttpMocker) -> None:
        """Test that CustomFieldTransformation converts cf_* fields to custom_fields array."""
        http_mocker.get(
            RequestBuilder.events_endpoint().with_any_query_params().build(),
            event_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)

        # Assert record exists
        assert len(output.records) == 1
        record_data = output.records[0].record.data

        # Assert cf_ fields are REMOVED from top level
        assert not any(
            key.startswith("cf_") for key in record_data.keys()
        ), "cf_ fields should be removed from record and moved to custom_fields array"

        # Assert custom_fields array EXISTS
        assert "custom_fields" in record_data, "custom_fields array should be created by CustomFieldTransformation"
        assert isinstance(record_data["custom_fields"], list)

        # Assert custom_fields array contains the transformed fields
        assert len(record_data["custom_fields"]) == 2, "custom_fields array should contain 2 transformed fields"

        # Verify structure and values of custom_fields items
        custom_fields = {cf["name"]: cf["value"] for cf in record_data["custom_fields"]}
        assert len(custom_fields) == 2, "Should have exactly 2 custom fields"

    @HttpMocker()
    def test_incremental_sync_with_state_and_params(self, http_mocker: HttpMocker) -> None:
        """
        Test incremental sync with prior state and validate request parameters.

        This test validates:
        1. State from previous sync is accepted
        2. Correct request parameters are sent (occurred_at[between] - NO sort_by or include_deleted for event stream)
        3. State advances to latest record's cursor value
        """
        # ARRANGE: Previous state from last sync
        previous_state_timestamp = 1704067200  # 2024-01-01T00:00:00
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"occurred_at": previous_state_timestamp}).build()

        # Mock API response with record AFTER the state timestamp
        # Note: Event stream uses sort_by[asc]=occurred_at and occurred_at[between], but NO include_deleted
        http_mocker.get(
            RequestBuilder.events_endpoint()
            .with_sort_by_asc("occurred_at")
            .with_occurred_at_between(previous_state_timestamp, 1705320000)  # Frozen time: 2024-01-15T12:00:00Z
            .with_limit(100)
            .build(),
            event_response(),
        )

        # ACT: Run incremental sync with state
        output = read_output(config_builder=config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental, state=state)

        # ASSERT: Records returned
        assert len(output.records) == 1, "Should return exactly 1 record"
        record = output.records[0].record.data

        # ASSERT: Record data is correct
        assert record["id"] == "ev_001"
        assert record["occurred_at"] >= previous_state_timestamp, "Record should be from after the state timestamp"

        # ASSERT: State message emitted
        assert len(output.state_messages) > 0, "Should emit state messages"

        # ASSERT: State advances to latest record
        latest_state = output.state_messages[-1].state.stream.stream_state
        latest_cursor_value = int(latest_state.__dict__["occurred_at"])

        # State should advance beyond previous state
        assert latest_cursor_value > previous_state_timestamp, f"State should advance: {latest_cursor_value} > {previous_state_timestamp}"

        # State should match the latest record's cursor value
        assert (
            latest_cursor_value == 1705312800
        ), f"State should be latest record's cursor value: expected 1705312800, got {latest_cursor_value}"

    @HttpMocker()
    def test_error_configuration_incompatible_ignored(self, http_mocker: HttpMocker) -> None:
        """Test configuration_incompatible error is ignored for event stream as configured in manifest."""
        http_mocker.get(
            RequestBuilder.events_endpoint().with_any_query_params().build(),
            configuration_incompatible_response(),
        )
        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)

        # Verify no records returned (error was ignored)
        assert len(output.records) == 0

        # Verify error message from manifest is logged
        assert output.is_in_logs("Stream is available only for Product Catalog 1.0")
