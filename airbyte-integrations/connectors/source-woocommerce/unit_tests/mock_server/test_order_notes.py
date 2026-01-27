# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the order_notes stream.

This stream is a substream of orders. It fetches notes for each order.
The path is /orders/{order_id}/notes.

Note: The parent orders stream uses DatetimeBasedCursor with modified_after/modified_before
parameters, so we need to freeze time and use the correct date parameters.
"""

import json
from pathlib import Path
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ConfigBuilder
from .request_builder import WooCommerceRequestBuilder
from .utils import config, read_output


_STREAM_NAME = "order_notes"


def _get_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "order_notes.json"
    return json.loads(template_path.read_text())


def _get_orders_response_template() -> list:
    template_path = Path(__file__).parent.parent / "resource" / "http" / "response" / "orders.json"
    return json.loads(template_path.read_text())


class TestOrderNotesFullRefresh(TestCase):
    """
    Tests for the order_notes stream in full refresh mode.

    The order_notes stream is a substream of orders. It uses SubstreamPartitionRouter
    to fetch notes for each order returned by the parent orders stream.

    Note: The parent orders stream uses DatetimeBasedCursor, so we need to freeze time
    and mock the orders endpoint with the correct modified_after/modified_before parameters.
    """

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
    def test_read_records_single_parent(self, http_mocker: HttpMocker) -> None:
        """Test reading order notes for a single parent order."""
        orders_response = _get_orders_response_template()
        order_id = orders_response[0]["id"]

        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(orders_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.order_notes_endpoint(order_id).with_default_params().build(),
            HttpResponse(body=json.dumps(_get_response_template()), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 281
        assert output.records[0].record.data["note"] == "Payment received via Stripe."

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_multiple_parents(self, http_mocker: HttpMocker) -> None:
        """
        Test reading order notes for multiple parent orders.

        This tests the substream behavior with at least 2 parent records.
        """
        orders_template = _get_orders_response_template()[0]
        orders_response = [
            {**orders_template, "id": 727},
            {**orders_template, "id": 728},
        ]

        notes_for_727 = [
            {
                "id": 1,
                "note": "Note for order 727",
                "date_created": "2024-03-15T10:30:00",
                "date_created_gmt": "2024-03-15T10:30:00",
                "author": "system",
                "customer_note": False,
            }
        ]
        notes_for_728 = [
            {
                "id": 2,
                "note": "Note for order 728",
                "date_created": "2024-03-15T11:00:00",
                "date_created_gmt": "2024-03-15T11:00:00",
                "author": "system",
                "customer_note": False,
            }
        ]

        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(orders_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.order_notes_endpoint(727).with_default_params().build(),
            HttpResponse(body=json.dumps(notes_for_727), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.order_notes_endpoint(728).with_default_params().build(),
            HttpResponse(body=json.dumps(notes_for_728), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 2
        notes = [r.record.data["note"] for r in output.records]
        assert "Note for order 727" in notes
        assert "Note for order 728" in notes

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_empty_parent(self, http_mocker: HttpMocker) -> None:
        """Test reading when there are no parent orders."""
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
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_empty_notes(self, http_mocker: HttpMocker) -> None:
        """Test reading when parent order has no notes."""
        orders_response = _get_orders_response_template()
        order_id = orders_response[0]["id"]

        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(orders_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.order_notes_endpoint(order_id).with_default_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 0

    @HttpMocker()
    @freezegun.freeze_time("2024-01-15T12:00:00Z")
    def test_read_records_pagination(self, http_mocker: HttpMocker) -> None:
        """
        Test pagination for order notes.

        The connector uses OffsetIncrement pagination with page_size=100.
        """
        orders_response = _get_orders_response_template()
        order_id = orders_response[0]["id"]

        notes_template = {
            "id": 1,
            "note": "Test note",
            "date_created": "2024-03-15T10:30:00",
            "date_created_gmt": "2024-03-15T10:30:00",
            "author": "system",
            "customer_note": False,
        }

        page1_notes = []
        for i in range(100):
            note = notes_template.copy()
            note["id"] = i + 1
            page1_notes.append(note)

        page2_notes = []
        for i in range(50):
            note = notes_template.copy()
            note["id"] = 101 + i
            page2_notes.append(note)

        http_mocker.get(
            WooCommerceRequestBuilder.orders_endpoint()
            .with_default_params()
            .with_modified_after("2024-01-01T00:00:00")
            .with_modified_before("2024-01-15T12:00:00")
            .build(),
            HttpResponse(body=json.dumps(orders_response), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.order_notes_endpoint(order_id).with_default_params().build(),
            HttpResponse(body=json.dumps(page1_notes), status_code=200),
        )
        http_mocker.get(
            WooCommerceRequestBuilder.order_notes_endpoint(order_id).with_default_params().with_offset(100).build(),
            HttpResponse(body=json.dumps(page2_notes), status_code=200),
        )

        output = self._read(config_=config().with_start_date("2024-01-01"))
        assert len(output.records) == 150
