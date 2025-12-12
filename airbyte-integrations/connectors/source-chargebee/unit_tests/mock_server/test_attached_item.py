# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .request_builder import RequestBuilder
from .response_builder import (
    attached_item_response,
    configuration_incompatible_response,
    item_response,
    item_response_multiple,
)
from .utils import config, read_output


_STREAM_NAME = "attached_item"


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
