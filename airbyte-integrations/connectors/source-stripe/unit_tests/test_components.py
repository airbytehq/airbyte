# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import MagicMock

import pytest

from components import InvoiceLineItemsEventExtractor


def _make_response(body: dict) -> MagicMock:
    response = MagicMock()
    response.json.return_value = body
    response.content = json.dumps(body).encode()
    response.headers = {"Content-Type": "application/json"}
    response.status_code = 200
    response.encoding = "utf-8"
    response.text = json.dumps(body)
    return response


def _make_extractor() -> InvoiceLineItemsEventExtractor:
    return InvoiceLineItemsEventExtractor(config={}, parameters={})


def _make_event(
    event_type: str = "invoice.updated",
    event_id: str = "evt_1",
    updated: int = 1700000000,
    created: int = 1699000000,
    invoice_id: str = "in_123",
    invoice_created: int = 1698000000,
    lines_data: list | None = None,
    lines_has_more: bool = False,
    include_lines: bool = True,
) -> dict:
    invoice: dict = {
        "id": invoice_id,
        "object": "invoice",
        "created": invoice_created,
    }
    if include_lines:
        invoice["lines"] = {
            "object": "list",
            "data": lines_data if lines_data is not None else [],
            "has_more": lines_has_more,
            "total_count": len(lines_data) if lines_data is not None else 0,
            "url": f"/v1/invoices/{invoice_id}/lines",
        }
    return {
        "id": event_id,
        "type": event_type,
        "created": created,
        "updated": updated,
        "data": {"object": invoice},
    }


def _make_line_item(line_item_id: str = "il_1", amount: int = 1000) -> dict:
    return {"id": line_item_id, "object": "line_item", "amount": amount}


@pytest.mark.parametrize(
    "events,expected_records",
    [
        pytest.param(
            [
                _make_event(
                    lines_data=[_make_line_item("il_1", 1000), _make_line_item("il_2", 2000)],
                ),
            ],
            [
                {
                    "id": "il_1",
                    "object": "line_item",
                    "amount": 1000,
                    "invoice_id": "in_123",
                    "invoice_created": 1698000000,
                    "invoice_updated": 1700000000,
                },
                {
                    "id": "il_2",
                    "object": "line_item",
                    "amount": 2000,
                    "invoice_id": "in_123",
                    "invoice_created": 1698000000,
                    "invoice_updated": 1700000000,
                },
            ],
            id="multiple_line_items_from_single_event",
        ),
        pytest.param(
            [_make_event(lines_data=[])],
            [],
            id="empty_lines_data",
        ),
        pytest.param(
            [_make_event(include_lines=False)],
            [],
            id="no_lines_field_on_invoice",
        ),
        pytest.param(
            [],
            [],
            id="no_events",
        ),
        pytest.param(
            [
                _make_event(
                    event_type="invoice.deleted",
                    lines_data=[_make_line_item("il_del")],
                ),
            ],
            [
                {
                    "id": "il_del",
                    "object": "line_item",
                    "amount": 1000,
                    "invoice_id": "in_123",
                    "invoice_created": 1698000000,
                    "invoice_updated": 1700000000,
                    "is_deleted": True,
                },
            ],
            id="deleted_event_marks_line_items",
        ),
        pytest.param(
            [_make_event(event_type="invoice.deleted", lines_data=[])],
            [],
            id="deleted_event_with_no_line_items_yields_nothing",
        ),
        pytest.param(
            [
                _make_event(
                    event_id="evt_1",
                    invoice_id="in_A",
                    lines_data=[_make_line_item("il_A1")],
                ),
                _make_event(
                    event_id="evt_2",
                    invoice_id="in_B",
                    lines_data=[_make_line_item("il_B1"), _make_line_item("il_B2")],
                ),
            ],
            [
                {
                    "id": "il_A1",
                    "object": "line_item",
                    "amount": 1000,
                    "invoice_id": "in_A",
                    "invoice_created": 1698000000,
                    "invoice_updated": 1700000000,
                },
                {
                    "id": "il_B1",
                    "object": "line_item",
                    "amount": 1000,
                    "invoice_id": "in_B",
                    "invoice_created": 1698000000,
                    "invoice_updated": 1700000000,
                },
                {
                    "id": "il_B2",
                    "object": "line_item",
                    "amount": 1000,
                    "invoice_id": "in_B",
                    "invoice_created": 1698000000,
                    "invoice_updated": 1700000000,
                },
            ],
            id="multiple_events_yield_all_line_items",
        ),
        pytest.param(
            [{"id": "evt_bad", "type": "invoice.updated", "data": {}}],
            [],
            id="event_with_no_object",
        ),
        pytest.param(
            [{"id": "evt_bad", "type": "invoice.updated", "data": {"object": "not_a_dict"}}],
            [],
            id="event_with_non_dict_object",
        ),
        pytest.param(
            [
                _make_event(
                    lines_data=[_make_line_item("il_1"), "not_a_dict", _make_line_item("il_2")],
                ),
            ],
            [
                {
                    "id": "il_1",
                    "object": "line_item",
                    "amount": 1000,
                    "invoice_id": "in_123",
                    "invoice_created": 1698000000,
                    "invoice_updated": 1700000000,
                },
                {
                    "id": "il_2",
                    "object": "line_item",
                    "amount": 1000,
                    "invoice_id": "in_123",
                    "invoice_created": 1698000000,
                    "invoice_updated": 1700000000,
                },
            ],
            id="non_dict_line_items_are_skipped",
        ),
    ],
)
def test_extract_records(events, expected_records):
    extractor = _make_extractor()
    response = _make_response({"data": events})
    records = list(extractor.extract_records(response))
    assert records == expected_records


def test_invoice_updated_uses_event_updated():
    extractor = _make_extractor()
    event = _make_event(updated=1700000000, created=1699000000, lines_data=[_make_line_item()])
    response = _make_response({"data": [event]})
    records = list(extractor.extract_records(response))
    assert records[0]["invoice_updated"] == 1700000000


def test_invoice_updated_falls_back_to_created():
    extractor = _make_extractor()
    event = _make_event(lines_data=[_make_line_item()])
    del event["updated"]
    response = _make_response({"data": [event]})
    records = list(extractor.extract_records(response))
    assert records[0]["invoice_updated"] == event["created"]


def test_invoice_updated_falls_back_to_now():
    extractor = _make_extractor()
    event = _make_event(lines_data=[_make_line_item()])
    del event["updated"]
    del event["created"]
    response = _make_response({"data": [event]})
    records = list(extractor.extract_records(response))
    assert isinstance(records[0]["invoice_updated"], int)
    assert records[0]["invoice_updated"] > 1700000000
