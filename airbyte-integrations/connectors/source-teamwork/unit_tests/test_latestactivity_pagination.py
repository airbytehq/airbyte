# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import yaml


_MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"


def _latestactivity_stream() -> dict:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    return manifest["definitions"]["streams"]["latestactivity"]


def test_latestactivity_uses_cursor_pagination_instead_of_offset_pagination() -> None:
    paginator = _latestactivity_stream()["retriever"]["paginator"]

    assert paginator["page_token_option"] == {
        "type": "RequestOption",
        "inject_into": "request_parameter",
        "field_name": "cursor",
    }
    assert paginator["page_size_option"] == {
        "type": "RequestOption",
        "inject_into": "request_parameter",
        "field_name": "limit",
    }
    assert paginator["pagination_strategy"]["type"] == "CursorPagination"
    assert paginator["pagination_strategy"]["page_size"] <= 500
    assert "nextCursor" in paginator["pagination_strategy"]["cursor_value"]
    assert "nextCursor" in paginator["pagination_strategy"]["stop_condition"]


def test_latestactivity_incremental_sync_filters_requests_with_updated_after() -> None:
    incremental_sync = _latestactivity_stream()["incremental_sync"]

    assert incremental_sync["start_time_option"] == {
        "type": "RequestOption",
        "field_name": "updatedAfter",
        "inject_into": "request_parameter",
    }
