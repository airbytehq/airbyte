# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import RequestBuilder
from .response_builder import gift_response
from .utils import config, read_output


_STREAM_NAME = "gift"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestGiftStream(TestCase):
    """Tests for the gift stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for gift stream."""
        http_mocker.get(
            RequestBuilder.gifts_endpoint().with_any_query_params().build(),
            gift_response(),
        )

        output = read_output(config_builder=config(), stream_name=_STREAM_NAME)
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "gift_001"

    @HttpMocker()
    def test_transformation_custom_fields(self, http_mocker: HttpMocker) -> None:
        """Test that CustomFieldTransformation converts cf_* fields to custom_fields array."""
        http_mocker.get(
            RequestBuilder.gifts_endpoint().with_any_query_params().build(),
            gift_response(),
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
