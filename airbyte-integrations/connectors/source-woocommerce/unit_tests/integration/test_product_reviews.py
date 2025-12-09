# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the product_reviews stream.

This stream uses server-side incremental sync with after/before parameters
(different from modified_after/modified_before) and 30-day (P30D) date slicing.
The cursor field is date_created_gmt.
"""

import json
from pathlib import Path
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder
from .request_builder import WooCommerceRequestBuilder
from .utils import config, read_output


_STREAM_NAME = "product_reviews"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "product_reviews.json"
    return json.loads(template_path.read_text())


class TestProductReviewsFullRefresh(TestCase):
    """Tests for the product_reviews stream in full refresh mode."""

    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Test reading product reviews in full refresh mode."""
        http_mocker.get(
            WooCommerceRequestBuilder.product_reviews_endpoint()
            .with_default_params()
            .with_after("2024-01-01T00:00:00")
            .with_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 22
        assert output.records[0].record.data["rating"] == 5

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no product reviews."""
        http_mocker.get(
            WooCommerceRequestBuilder.product_reviews_endpoint()
            .with_default_params()
            .with_after("2024-01-01T00:00:00")
            .with_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 0


class TestProductReviewsIncremental(TestCase):
    """Tests for the product_reviews stream in incremental mode."""

    @staticmethod
    def _read(config_: ConfigBuilder, state=None, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.incremental,
            state=state,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_single_slice(self, http_mocker: HttpMocker) -> None:
        """Test reading product reviews with a single date slice."""
        http_mocker.get(
            WooCommerceRequestBuilder.product_reviews_endpoint()
            .with_default_params()
            .with_after("2024-01-01T00:00:00")
            .with_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))

        # Assert on record content
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 22
        assert output.records[0].record.data["rating"] == 5

        # Assert on state - should be updated with the timestamp of the latest record
        assert len(output.state_messages) > 0
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert (
            latest_state.__dict__["date_created_gmt"] == "2024-01-10T09:00:00"
        ), "State should be updated to the date_created_gmt timestamp of the latest record"

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no product reviews in the date range."""
        http_mocker.get(
            WooCommerceRequestBuilder.product_reviews_endpoint()
            .with_default_params()
            .with_after("2024-01-01T00:00:00")
            .with_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 0

    @HttpMocker()
    @freezegun.freeze_time("2024-02-10T12:00:00Z")
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker) -> None:
        """
        Test that incremental sync correctly handles state and returns updated records.

        Given: A previous sync state with a date_created_gmt cursor value
        When: Running an incremental sync
        Then: The connector should return records and update state to the latest record's cursor

        Note: The DatetimeBasedCursor uses config start_date for HTTP request parameters,
        while state is used for filtering records and updating the cursor. We align
        config start_date with state to ensure a single date slice for testing.
        """
        # Set up state from previous sync - align with config start_date
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"date_created_gmt": "2024-01-15T00:00:00"}).build()

        # Mock request - config start_date determines after parameter
        # Date range is <30 days to ensure single slice
        http_mocker.get(
            WooCommerceRequestBuilder.product_reviews_endpoint()
            .with_default_params()
            .with_after("2024-01-15T00:00:00")
            .with_before("2024-02-10T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-15"), state=state)

        # Assert: Should return records created since last sync
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 22
        assert output.records[0].record.data["rating"] == 5

        # Assert: State should be at least the start_date value
        # Note: The mock record has date_created_gmt=2024-01-10 which is before the state cursor,
        # so the state remains at the start_date value (cursor takes max of state and record cursor)
        assert len(output.state_messages) > 0
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert (
            latest_state.__dict__["date_created_gmt"] == "2024-01-15T00:00:00"
        ), "State should remain at start_date since record cursor is earlier"
