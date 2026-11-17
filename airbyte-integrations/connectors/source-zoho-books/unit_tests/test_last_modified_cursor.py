# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Regression tests for Zoho Books document-stream incremental cursors."""

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_BASE_CONFIG = {
    "region": "com",
    "client_id": "client-id",
    "client_secret": "client-secret",
    "refresh_token": "refresh-token",
    "start_date": "2023-01-01T00:00:00Z",
}
_STREAMS = [
    pytest.param("invoices", "invoices", "invoice_id", id="invoices"),
    pytest.param("creditnotes", "creditnotes", "creditnote_id", id="creditnotes"),
    pytest.param("purchase_orders", "purchaseorders", "purchaseorder_id", id="purchase_orders"),
    pytest.param("sales_orders", "salesorders", "salesorder_id", id="sales_orders"),
]
_PRIOR_CURSOR = "2023-11-18T02:02:51-0800"
_NEW_CURSOR = "2023-11-19T02:02:51-0800"


def _read(stream_name: str, config: dict, state=None):
    """Read one stream incrementally from the declarative source."""
    source = get_source(config=config, state=state)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(source, config, catalog, state or [])


def _record(record_id: str, cursor: str) -> dict:
    """Build the minimum valid document record for the selected stream schema."""
    return {
        "invoice_id": record_id,
        "creditnote_id": record_id,
        "purchaseorder_id": record_id,
        "salesorder_id": record_id,
        "date": "2023-01-01",
        "last_modified_time": cursor,
    }


def _latest_cursor(output, stream_name: str):
    """Return the latest emitted cursor for a stream."""
    for message in reversed(output.state_messages):
        stream_state = message.state.stream
        if stream_state and stream_state.stream_descriptor.name == stream_name:
            return getattr(stream_state.stream_state, "last_modified_time", None)
    return None


@pytest.mark.parametrize("stream_name,response_key,primary_key", _STREAMS)
def test_incremental_sync_uses_last_modified_time_and_emits_edited_old_documents(stream_name, response_key, primary_key):
    """Requests use last_modified_time and emit records edited after the prior cursor."""
    config = {**_BASE_CONFIG}
    state = StateBuilder().with_stream_state(stream_name, {"last_modified_time": _PRIOR_CURSOR}).build()
    response = {response_key: [_record("edited-document", _NEW_CURSOR)]}
    api_url = f"https://www.zohoapis.com/books/v3/{response_key}"
    token_url = "https://accounts.zoho.com/oauth/v2/token"

    with requests_mock.Mocker(case_sensitive=True) as mocker:
        mocker.post(token_url, json={"access_token": "access-token", "expires_in": 3600})
        mocker.get(api_url, json=response)
        output = _read(stream_name, config, state)

    api_requests = [request for request in mocker.request_history if request.path == f"/books/v3/{response_key}"]
    assert len(api_requests) == 1
    request = api_requests[0]
    assert request.qs == {
        "page": ["1"],
        "per_page": ["200"],
        "last_modified_time": [_PRIOR_CURSOR],
    }
    assert "date_start" not in request.qs
    assert "date_end" not in request.qs
    assert [record.record.data[primary_key] for record in output.records] == ["edited-document"]
    assert _latest_cursor(output, stream_name) == _NEW_CURSOR
