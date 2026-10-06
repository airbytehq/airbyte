# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the customers stream.

This stream uses client-side incremental sync (is_client_side_incremental: true).
The API returns all records and the connector filters them client-side based on
the cursor field (date_modified_gmt).
"""

import json
from pathlib import Path
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder
from .request_builder import WooCommerceRequestBuilder
from .utils import config, read_output


_STREAM_NAME = "customers"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "customers.json"
    return json.loads(template_path.read_text())


class TestCustomersFullRefresh(TestCase):
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_read_records_single_page(self, http_mocker: HttpMocker) -> None:
        """
        Test reading a single page of customers.

        Note: The connector only fetches more pages if the first page returns
        page_size (100) records. Since our mock returns only 1 record, it won't
        try to fetch the second page.
        """
        http_mocker.get(
            WooCommerceRequestBuilder.customers_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1
        assert output.records[0].record.data["email"] == "john.doe@example.com"
        assert output.records[0].record.data["first_name"] == "John"
        assert output.records[0].record.data["last_name"] == "Doe"

    @HttpMocker()
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            WooCommerceRequestBuilder.customers_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config())
        assert len(output.records) == 0


class TestCustomersIncremental(TestCase):
    """
    Tests for the customers stream in incremental mode.

    The customers stream uses client-side incremental sync (is_client_side_incremental: true),
    so the API returns all records and the connector filters them client-side based on
    the cursor field (date_modified_gmt). Unlike orders/products, no date parameters
    are sent to the API.
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
    def test_read_records_single_slice(self, http_mocker: HttpMocker) -> None:
        """
        Test reading customers in incremental mode.

        Unlike orders/products which use server-side incremental with date parameters,
        customers uses client-side incremental. The API returns all records and the
        connector filters them locally based on the cursor field.
        """
        http_mocker.get(
            WooCommerceRequestBuilder.customers_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))

        # Assert on record content
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1
        assert output.records[0].record.data["email"] == "john.doe@example.com"
        assert output.records[0].record.data["first_name"] == "John"
        assert output.records[0].record.data["last_name"] == "Doe"

        # Assert on state - should be updated with the timestamp of the latest record
        assert len(output.state_messages) > 0
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert (
            latest_state.__dict__["date_modified_gmt"] == "2024-03-01T15:20:00"
        ), "State should be updated to the date_modified_gmt timestamp of the latest record"

    @HttpMocker()
    def test_read_records_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no customers."""
        http_mocker.get(
            WooCommerceRequestBuilder.customers_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 0

    @HttpMocker()
    def test_incremental_sync_with_state(self, http_mocker: HttpMocker) -> None:
        """
        Test incremental sync with previous state for customers stream.

        Customers is a client-side incremental stream (is_client_side_incremental: true).
        This test validates:
        - Connector accepts state from previous sync
        - Records from API are emitted (client-side filtering based on cursor)
        - State is updated to latest record's date_modified_gmt

        NOTE: Unlike server-side incremental streams (orders, products), customers
        does NOT have date parameters in the API request. All records are returned
        and filtering happens client-side.
        """
        # ARRANGE - Previous state from last sync (earlier than record's date_modified_gmt)
        previous_state_date = "2024-01-01T00:00:00"
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"date_modified_gmt": previous_state_date}).build()

        # Mock returns customer (date_modified_gmt = 2024-03-01, after state 01-01)
        # No date params in request since this is client-side incremental
        http_mocker.get(
            WooCommerceRequestBuilder.customers_endpoint().with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        # ACT - Pass state to read
        output = self._read(config_=config().with_start_date("2024-01-01"), state=state)

        # ASSERT - Records returned (customer's date_modified_gmt is after state)
        assert len(output.records) == 1, f"Expected 1 record, got {len(output.records)}"

        # ASSERT - Verify record content
        record = output.records[0].record.data
        assert record["id"] == 1, f"Expected id 1, got {record['id']}"
        assert record["email"] == "john.doe@example.com"
        assert record["date_modified_gmt"] == "2024-03-01T15:20:00"

        # ASSERT - State message with latest date_modified_gmt
        assert len(output.state_messages) > 0, "Expected state messages to be emitted"
        latest_state = output.state_messages[-1].state.stream.stream_state
        assert (
            latest_state.__dict__["date_modified_gmt"] == "2024-03-01T15:20:00"
        ), f"Expected state to advance to latest record, got {latest_state.__dict__}"
