# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Regression tests for Gorgias incremental data-feed pagination."""

from urllib.parse import unquote

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_BASE_CONFIG = {
    "username": "test-username",
    "password": "test-password",
    "domain_name": "test-domain",
    "start_date": "2026-01-01T00:00:00Z",
}
_BASE_URL = "https://test-domain.gorgias.com/api"
_CURSOR = "2026-08-10T00:00:00.000000+0000"


def _record(record_id: int, cursor: str) -> dict:
    return {"id": record_id, "updated_datetime": cursor, "created_datetime": cursor}


def _read(stream_name: str, state: list):
    source = get_source(config=_BASE_CONFIG, state=state)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(source, _BASE_CONFIG, catalog, state)


def _stream_state(stream_name: str, cursor_field: str = "updated_datetime") -> list:
    return StateBuilder().with_stream_state(stream_name, {cursor_field: _CURSOR}).build()


def _latest_cursor_value(output, stream_name: str, cursor_field: str):
    for message in reversed(output.state_messages):
        stream_state = message.state.stream
        if stream_state and stream_state.stream_descriptor.name == stream_name:
            return getattr(stream_state.stream_state, cursor_field, None)
    return None


def test_tickets_incremental_data_feed_filters_records_and_stops_pagination():
    page_1 = {
        "data": [
            _record(1, "2026-08-12T00:00:00.000000+0000"),
            _record(2, "2026-08-11T00:00:00.000000+0000"),
        ],
        "meta": {"next_cursor": "page-2"},
    }
    page_2 = {
        "data": [
            _record(3, "2026-08-10T00:00:00.000000+0000"),
            _record(4, "2026-08-09T00:00:00.000000+0000"),
        ],
        "meta": {"next_cursor": "page-3"},
    }
    page_3 = {
        "data": [_record(5, "2026-08-08T00:00:00.000000+0000")],
        "meta": {"next_cursor": None},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/tickets", [{"json": page_1}, {"json": page_2}, {"json": page_3}])
        output = _read("tickets", _stream_state("tickets"))

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1, 2, 3]
    ticket_requests = [request for request in mocker.request_history if request.path == "/api/tickets"]
    assert len(ticket_requests) == 2
    assert ticket_requests[0].qs["order_by"] == ["updated_datetime:desc"]
    assert _latest_cursor_value(output, "tickets", "updated_datetime") == "2026-08-12T00:00:00.000000+0000"


def test_events_incremental_request_uses_lookback_and_client_side_filtering():
    page = {
        "data": [
            _record(1, "2026-08-12T00:00:00.000000+0000"),
            _record(2, "2026-08-10T00:00:00.000000+0000"),
            _record(3, "2026-08-09T23:59:00.000000+0000"),
        ],
        "meta": {"next_cursor": None},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/events", json=page)
        output = _read("events", _stream_state("events", "created_datetime"))

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1, 2]
    event_requests = [request for request in mocker.request_history if request.path == "/api/events"]
    assert len(event_requests) == 1
    assert "created_datetime[gte]=2026-08-09T23:55:00Z" in unquote(event_requests[0].url)
    assert "order_by" not in event_requests[0].qs


def test_events_cold_start_request_uses_configured_start_date():
    pages = [
        {
            "data": [_record(1, "2026-01-02T00:00:00.000000+0000")],
            "meta": {"next_cursor": "page-2"},
        },
        {
            "data": [_record(2, "2026-01-01T00:00:00.000000+0000")],
            "meta": {"next_cursor": None},
        },
    ]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/events", [{"json": page} for page in pages])
        output = _read("events", [])

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1, 2]
    event_requests = [request for request in mocker.request_history if request.path == "/api/events"]
    assert len(event_requests) == 2
    assert "created_datetime[gte]=2026-01-01T00:00:00Z" in unquote(event_requests[0].url)
    assert "order_by" not in event_requests[0].qs


def test_messages_incremental_data_feed_filters_records_and_stops_pagination():
    page_1 = {
        "data": [
            _record(1, "2026-08-12T00:00:00.000000+0000"),
            _record(2, "2026-08-10T00:00:00.000000+0000"),
        ],
        "meta": {"next_cursor": "page-2"},
    }
    page_2 = {
        "data": [
            _record(3, "2026-08-09T00:00:00.000000+0000"),
            _record(4, "2026-08-08T00:00:00.000000+0000"),
        ],
        "meta": {"next_cursor": "page-3"},
    }
    page_3 = {
        "data": [_record(5, "2026-07-10T00:00:00.000000+0000")],
        "meta": {"next_cursor": None},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/messages", [{"json": page_1}, {"json": page_2}, {"json": page_3}])
        output = _read("messages", _stream_state("messages", "created_datetime"))

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1, 2]
    message_requests = [request for request in mocker.request_history if request.path == "/api/messages"]
    assert len(message_requests) == 2
    assert message_requests[0].qs["order_by"] == ["created_datetime:desc"]
    assert _latest_cursor_value(output, "messages", "created_datetime") == "2026-08-12T00:00:00.000000+0000"


def test_tickets_ascending_response_stops_before_emitting_records():
    page_1 = {
        "data": [
            _record(1, "2026-08-08T00:00:00.000000+0000"),
            _record(2, "2026-08-09T00:00:00.000000+0000"),
        ],
        "meta": {"next_cursor": "page-2"},
    }
    page_2 = {
        "data": [_record(3, "2026-08-12T00:00:00.000000+0000")],
        "meta": {"next_cursor": None},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/tickets", [{"json": page_1}, {"json": page_2}])
        output = _read("tickets", _stream_state("tickets"))

    assert output.records == []
    ticket_requests = [request for request in mocker.request_history if request.path == "/api/tickets"]
    assert len(ticket_requests) == 1


def test_tickets_data_feed_cold_start_walks_from_configured_start_date():
    pages = [
        {
            "data": [_record(1, "2026-01-02T00:00:00.000000+0000")],
            "meta": {"next_cursor": "page-2"},
        },
        {
            "data": [_record(2, "2026-01-01T00:00:00.000000+0000")],
            "meta": {"next_cursor": None},
        },
    ]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/tickets", [{"json": page} for page in pages])
        output = _read("tickets", [])

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1, 2]
    ticket_requests = [request for request in mocker.request_history if request.path == "/api/tickets"]
    assert len(ticket_requests) == 2
    assert ticket_requests[0].qs["order_by"] == ["updated_datetime:desc"]


def test_tags_incremental_data_feed_filters_records_and_stops_pagination():
    page_1 = {
        "data": [
            _record(1, "2026-08-12T00:00:00.000000+0000"),
            _record(2, "2026-08-11T00:00:00.000000+0000"),
        ],
        "meta": {"next_cursor": "page-2"},
    }
    page_2 = {
        "data": [
            _record(3, "2026-08-09T00:00:00.000000+0000"),
            _record(4, "2026-08-08T00:00:00.000000+0000"),
        ],
        "meta": {"next_cursor": "page-3"},
    }
    page_3 = {
        "data": [_record(5, "2026-08-07T00:00:00.000000+0000")],
        "meta": {"next_cursor": None},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/tags", [{"json": page_1}, {"json": page_2}, {"json": page_3}])
        output = _read("tags", _stream_state("tags", "created_datetime"))

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1, 2]
    tag_requests = [request for request in mocker.request_history if request.path == "/api/tags"]
    assert len(tag_requests) == 2
    assert tag_requests[0].qs["order_by"] == ["created_datetime:desc"]
    assert _latest_cursor_value(output, "tags", "created_datetime") == "2026-08-12T00:00:00.000000+0000"


def test_macros_reads_full_history_on_every_sync():
    """`macros` is deliberately not a data feed.

    The stream fits in a single page, so a stop condition saves no requests, while the object's
    `updated_datetime` moves on every edit and `created_datetime` — the only field the endpoint can
    order by — does not. Reading in full is what keeps macro edits arriving.
    """
    pages = [
        {
            "data": [
                _record(1, "2026-08-12T00:00:00.000000+0000"),
                _record(2, "2026-08-09T00:00:00.000000+0000"),
            ],
            "meta": {"next_cursor": "page-2"},
        },
        {
            "data": [_record(3, "2026-08-08T00:00:00.000000+0000")],
            "meta": {"next_cursor": None},
        },
    ]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/macros", [{"json": page} for page in pages])
        output = _read("macros", _stream_state("macros", "created_datetime"))

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1, 2, 3]
    macro_requests = [request for request in mocker.request_history if request.path == "/api/macros"]
    assert len(macro_requests) == 2
    assert "order_by" not in macro_requests[0].qs


def test_integrations_client_side_incremental_filters_records_without_stopping_pagination():
    pages = [
        {
            "data": [
                _record(1, "2026-08-12T00:00:00.000000+0000"),
                _record(2, "2026-08-10T00:00:00.000000+0000"),
            ],
            "meta": {"next_cursor": "page-2"},
        },
        {
            "data": [_record(3, "2026-08-09T00:00:00.000000+0000")],
            "meta": {"next_cursor": "page-3"},
        },
        {
            "data": [_record(4, "2026-08-08T00:00:00.000000+0000")],
            "meta": {"next_cursor": None},
        },
    ]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/integrations", [{"json": page} for page in pages])
        output = _read("integrations", _stream_state("integrations"))

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1, 2]
    integration_requests = [request for request in mocker.request_history if request.path == "/api/integrations"]
    assert len(integration_requests) == 3
    assert "order_by" not in integration_requests[0].qs
    assert _latest_cursor_value(output, "integrations", "updated_datetime") == ("2026-08-12T00:00:00.000000+0000")
