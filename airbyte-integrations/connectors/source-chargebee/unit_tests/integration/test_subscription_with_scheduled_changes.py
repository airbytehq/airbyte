# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .request_builder import RequestBuilder
from .response_builder import (
    error_no_scheduled_changes_response,
    subscription_response,
    subscription_response_multiple,
    subscription_with_scheduled_changes_response,
)
from .utils import config, read_output


_STREAM_NAME = "subscription_with_scheduled_changes"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestSubscriptionWithScheduledChangesStream(TestCase):
    """Tests for the subscription_with_scheduled_changes stream (substream of subscription)."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for subscription_with_scheduled_changes stream."""
        http_mocker.get(
            RequestBuilder.subscriptions_endpoint().with_any_query_params().build(),
            subscription_response(),
        )
        http_mocker.get(
            RequestBuilder.subscription_scheduled_changes_endpoint("sub_001").with_any_query_params().build(),
            subscription_with_scheduled_changes_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) >= 1
        assert output.records[0].record.data["id"] == "sub_001"

    @HttpMocker()
    def test_with_multiple_parents(self, http_mocker: HttpMocker) -> None:
        """Test subscription_with_scheduled_changes substream with multiple parent subscriptions."""
        http_mocker.get(
            RequestBuilder.subscriptions_endpoint().with_any_query_params().build(),
            subscription_response_multiple(),
        )
        http_mocker.get(
            RequestBuilder.subscription_scheduled_changes_endpoint("sub_001").with_any_query_params().build(),
            subscription_with_scheduled_changes_response(),
        )
        http_mocker.get(
            RequestBuilder.subscription_scheduled_changes_endpoint("sub_002").with_any_query_params().build(),
            subscription_with_scheduled_changes_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) >= 2

    @HttpMocker()
    def test_error_no_scheduled_changes_ignored(self, http_mocker: HttpMocker) -> None:
        """Test that 'No changes are scheduled' error is ignored (IGNORE action with error_message_contains)."""
        http_mocker.get(
            RequestBuilder.subscriptions_endpoint().with_any_query_params().build(),
            subscription_response(),
        )
        http_mocker.get(
            RequestBuilder.subscription_scheduled_changes_endpoint("sub_001").with_any_query_params().build(),
            error_no_scheduled_changes_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 0

    @HttpMocker()
    def test_both_transformations(self, http_mocker: HttpMocker) -> None:
        """
        Test that BOTH transformations work together:
        1. AddFields adds subscription_id from parent stream slice
        2. CustomFieldTransformation converts cf_* fields to custom_fields array
        """
        # Mock parent subscription stream
        http_mocker.get(
            RequestBuilder.subscriptions_endpoint().with_any_query_params().build(),
            subscription_response(),
        )

        # Mock subscription_with_scheduled_changes substream (with cf_ fields)
        http_mocker.get(
            RequestBuilder.subscription_scheduled_changes_endpoint("sub_001").with_any_query_params().build(),
            subscription_with_scheduled_changes_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)

        assert len(output.records) >= 1
        record_data = output.records[0].record.data

        # ========== Test Transformation #1: AddFields ==========
        assert "subscription_id" in record_data, "AddFields transformation should add subscription_id field"
        assert record_data["subscription_id"] == "sub_001", "subscription_id should match parent stream's id"

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

        # Mock parent subscription stream with state params
        http_mocker.get(
            RequestBuilder.subscriptions_endpoint()
            .with_sort_by_asc("updated_at")
            .with_include_deleted("true")
            .with_updated_at_between(previous_state_timestamp, 1705320000)  # Frozen time: 2024-01-15T12:00:00Z
            .with_limit(100)
            .build(),
            subscription_response(),
        )

        # Mock subscription_with_scheduled_changes substream
        http_mocker.get(
            RequestBuilder.subscription_scheduled_changes_endpoint("sub_001").with_any_query_params().build(),
            subscription_with_scheduled_changes_response(),
        )

        # ACT: Run incremental sync with state
        output = read_output(config_builder=config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental, state=state)

        # ASSERT: Records returned
        assert len(output.records) >= 1, "Should return at least 1 record"
        record = output.records[0].record.data

        # ASSERT: Record data is correct
        assert record["id"] == "sub_001"
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
