# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .request_builder import RequestBuilder
from .response_builder import (
    attached_item_response,
    configuration_incompatible_response,
    item_response,
    item_response_multiple,
)
from .utils import catalog, config, get_source, read_output


_STREAM_NAME = "attached_item"
_FROZEN_NOW_EPOCH = 1705320000  # 2024-01-15T12:00:00Z


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestAttachedItemStream(TestCase):
    """Tests for the attached_item stream (substream of item)."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for attached_item stream (substream of item)."""
        http_mocker.get(
            RequestBuilder.items_endpoint().with_any_query_params().build(),
            item_response(),
        )
        http_mocker.get(
            RequestBuilder.item_attached_items_endpoint("item_001").with_any_query_params().build(),
            attached_item_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "attached_001"

    @HttpMocker()
    def test_with_multiple_parents(self, http_mocker: HttpMocker) -> None:
        """Test attached_item substream with multiple parent items."""
        http_mocker.get(
            RequestBuilder.items_endpoint().with_any_query_params().build(),
            item_response_multiple(),
        )
        http_mocker.get(
            RequestBuilder.item_attached_items_endpoint("item_001").with_any_query_params().build(),
            attached_item_response(),
        )
        http_mocker.get(
            RequestBuilder.item_attached_items_endpoint("item_002").with_any_query_params().build(),
            attached_item_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 2

    @HttpMocker()
    def test_transformation_custom_fields(self, http_mocker: HttpMocker) -> None:
        """Test that CustomFieldTransformation converts cf_* fields to custom_fields array."""
        # Mock parent item stream
        http_mocker.get(
            RequestBuilder.items_endpoint().with_any_query_params().build(),
            item_response(),
        )

        # Mock attached_item substream (with cf_ fields)
        http_mocker.get(
            RequestBuilder.item_attached_items_endpoint("item_001").with_any_query_params().build(),
            attached_item_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)

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
    def test_error_configuration_incompatible_ignored(self, http_mocker: HttpMocker) -> None:
        """Test configuration_incompatible error is ignored for attached_item stream as configured in manifest."""
        # Mock parent stream (item) to return successfully
        http_mocker.get(
            RequestBuilder.items_endpoint().with_any_query_params().build(),
            item_response(),
        )

        # Mock attached_item substream to return CONFIG_INCOMPATIBLE
        http_mocker.get(
            RequestBuilder.item_attached_items_endpoint("item_001").with_any_query_params().build(),
            configuration_incompatible_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)

        # Verify no records returned (error was ignored)
        assert len(output.records) == 0

        # Verify error message from manifest is logged
        assert output.is_in_logs("Stream is available only for Product Catalog 1.0")

    @HttpMocker()
    def test_full_refresh_does_not_send_updated_at_filter(self, http_mocker: HttpMocker) -> None:
        """Full refresh sends no updated_at filter on attached_items requests."""
        http_mocker.get(
            RequestBuilder.items_endpoint().with_any_query_params().build(),
            item_response_multiple(),
        )
        # Exact match: only the limit param, no updated_at[between]
        for item_id in ("item_001", "item_002"):
            http_mocker.get(
                RequestBuilder.item_attached_items_endpoint(item_id).with_limit(100).build(),
                attached_item_response(),
            )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)

        assert len(output.records) == 2

    @HttpMocker()
    def test_incremental_first_sync_without_state_reads_all_and_emits_state(self, http_mocker: HttpMocker) -> None:
        """First incremental sync (no state) reads all attached items: no updated_at filter is sent."""
        http_mocker.get(
            RequestBuilder.items_endpoint().with_any_query_params().build(),
            item_response_multiple(),
        )
        # Exact match: slice start is epoch 0, so updated_at[between] must be omitted
        for item_id in ("item_001", "item_002"):
            http_mocker.get(
                RequestBuilder.item_attached_items_endpoint(item_id).with_limit(100).build(),
                attached_item_response(),
            )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

        assert len(output.records) == 2
        assert len(output.state_messages) > 0

        stream_state = dict(output.state_messages[-1].state.stream.stream_state.__dict__)
        assert stream_state["use_global_cursor"] is True
        assert int(stream_state["state"]["updated_at"]) == 1705312800  # from attached_item.json

    @HttpMocker()
    def test_incremental_with_state_sends_updated_at_between_per_item(self, http_mocker: HttpMocker) -> None:
        """Incremental sync with global state sends updated_at[between] for each parent item partition."""
        previous_state_timestamp = 1704067200  # 2024-01-01T00:00:00
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "use_global_cursor": True,
                    "state": {"updated_at": previous_state_timestamp},
                    "lookback_window": 0,
                },
            )
            .build()
        )
        _config = config().build()
        # ConcurrentPerPartitionCursor only consumes state when the source is built with it
        source = get_source(config=_config, state=state)

        http_mocker.get(
            RequestBuilder.items_endpoint().with_any_query_params().build(),
            item_response_multiple(),
        )
        for item_id in ("item_001", "item_002"):
            http_mocker.get(
                RequestBuilder.item_attached_items_endpoint(item_id)
                .with_limit(100)
                .with_updated_at_between(previous_state_timestamp, _FROZEN_NOW_EPOCH)
                .build(),
                attached_item_response(),
            )

        output = read(
            source,
            _config,
            catalog(_STREAM_NAME, SyncMode.incremental),
            state,
        )

        assert len(output.records) == 2
        assert len(output.state_messages) > 0

        stream_state = dict(output.state_messages[-1].state.stream.stream_state.__dict__)
        assert int(stream_state["state"]["updated_at"]) > previous_state_timestamp

    def test_discover_attached_item_supports_incremental(self) -> None:
        """Discover must advertise incremental sync with a source-defined updated_at cursor."""
        _config = config().build()
        source = get_source(config=_config)
        catalog = {stream.name: stream for stream in source.discover(logging.getLogger("test"), _config).streams}

        stream = catalog[_STREAM_NAME]
        assert SyncMode.incremental in stream.supported_sync_modes
        assert stream.source_defined_cursor is True
        assert stream.default_cursor_field == ["updated_at"]
