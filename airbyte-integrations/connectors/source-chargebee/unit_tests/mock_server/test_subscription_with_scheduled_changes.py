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
        assert len(output.records) == 1
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
        assert len(output.records) == 2

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

        # Verify no records returned (error was ignored)
        assert len(output.records) == 0

        # Verify error message from manifest is logged
        assert output.is_in_logs("No scheduled changes for subscription.")

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

        assert len(output.records) == 1
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
