# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import RequestBuilder
from .response_builder import (
    event_response,
    event_response_page1,
    event_response_page2,
)
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
    def test_pagination_two_pages(self, http_mocker: HttpMocker) -> None:
        """Test pagination with 2 pages for event stream."""
        http_mocker.get(
            RequestBuilder.events_endpoint().with_any_query_params().build(),
            [
                event_response_page1(),
                event_response_page2(),
            ],
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 2

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
        assert not any(key.startswith("cf_") for key in record_data.keys()), \
            "cf_ fields should be removed from record and moved to custom_fields array"

        # Assert custom_fields array EXISTS
        assert "custom_fields" in record_data, \
            "custom_fields array should be created by CustomFieldTransformation"
        assert isinstance(record_data["custom_fields"], list)

        # Assert custom_fields array contains the transformed fields
        assert len(record_data["custom_fields"]) == 2, \
            "custom_fields array should contain 2 transformed fields"

        # Verify structure and values of custom_fields items
        custom_fields = {cf["name"]: cf["value"] for cf in record_data["custom_fields"]}
        assert len(custom_fields) == 2, \
            "Should have exactly 2 custom fields"
