# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import RequestBuilder
from .response_builder import (
    attached_item_response,
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
        assert len(output.records) >= 1
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
        assert len(output.records) >= 2
