# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the orders stream.

This stream uses server-side incremental sync with modified_after/modified_before
parameters and 30-day (P30D) date slicing. The DatetimeBasedCursor calculates
date ranges based on the current time, so we use freezegun to freeze time.
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
from .response_builder import ResponseBuilder
from .utils import config, read_output


_STREAM_NAME = "orders"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "orders.json"
    return json.loads(template_path.read_text())


class TestOrdersFullRefresh(TestCase):
    """Tests for the orders stream in full refresh mode."""

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
        """Test reading orders in full refresh mode."""
        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 727
        assert output.records[0].record.data["status"] == "processing"

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no orders."""
        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 0


class TestOrdersIncremental(TestCase):
    """
    Tests for the orders stream in incremental mode.

    The orders stream uses DatetimeBasedCursor with:
    - step: P30D (30 days)
    - cursor_granularity: PT1S (1 second)
    - start_time_option: modified_after
    - end_time_option: modified_before
    """

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
        """
        Test reading orders with a single date slice.

        With start_date=2024-01-01 and frozen time=2024-01-15T12:00:00Z,
        the cursor should create a single slice from 2024-01-01 to 2024-01-15.
        """
        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )
        # Note: No second page mock needed because the connector only fetches more pages
        # if the first page returns page_size (100) records. Since our mock returns only
        # 1 record, it won't try to fetch the second page.

        output = self._read(config_=config().with_start_date("2024-01-01"))

        # Assert on record content
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 727
        assert output.records[0].record.data["status"] == "processing"

        # Assert on state - should be updated with the timestamp of the latest record
        assert len(output.state_messages) > 0
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert (
            latest_state.__dict__["date_modified_gmt"] == "2024-03-15T14:45:00"
        ), "State should be updated to the date_modified_gmt timestamp of the latest record"

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no orders in the date range."""
        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
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

        Given: A previous sync state with a date_modified_gmt cursor value
        When: Running an incremental sync
        Then: The connector should return records and update state to the latest record's cursor

        Note: The DatetimeBasedCursor uses config start_date for HTTP request parameters,
        while state is used for filtering records and updating the cursor. We align
        config start_date with state to ensure a single date slice for testing.
        """
        # Set up state from previous sync - align with config start_date
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"date_modified_gmt": "2024-01-15T00:00:00"}).build()

        # Mock request - config start_date determines modified_after parameter
        # Date range is <30 days to ensure single slice
        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-15T00:00:00")
            .with_modified_before("2024-02-10T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-15"), state=state)

        # Assert: Should return records updated since last sync
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 727
        assert output.records[0].record.data["status"] == "processing"

        # Assert: State should be updated with the timestamp of the latest record
        assert len(output.state_messages) > 0
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert (
            latest_state.__dict__["date_modified_gmt"] == "2024-03-15T14:45:00"
        ), "State should be updated to the date_modified_gmt timestamp of the latest record"

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_with_pagination(self, http_mocker: HttpMocker) -> None:
        """
        Test reading orders with pagination using OffsetIncrement.

        The connector uses OffsetIncrement pagination with page_size=100.
        When the first page returns exactly 100 records, the connector
        fetches the next page with offset=100. Pagination stops when
        a page returns fewer than 100 records.

        Note: This test validates the pagination behavior for all streams in this connector,
        as they all use the same default paginator (OffsetIncrement with page_size=100).
        Testing pagination here and in test_products.py is sufficient to verify the
        pagination configuration works correctly across the entire connector.
        """
        page_size = 100

        first_page_response = ResponseBuilder.from_template("orders").with_record_count(page_size, id_start=1).build()
        second_page_response = ResponseBuilder.from_template("orders").with_record_count(50, id_start=101).build()

        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(first_page_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .with_offset(100)
            .build(),
            HttpResponse(body=json.dumps(second_page_response), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))

        assert len(output.records) == 150
        assert output.records[0].record.data["id"] == 1
        assert output.records[99].record.data["id"] == 100
        assert output.records[100].record.data["id"] == 101
        assert output.records[149].record.data["id"] == 150
