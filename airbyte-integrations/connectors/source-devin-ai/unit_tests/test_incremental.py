#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""Unit tests for source-devin-ai incremental sync support.

These tests verify that the `sessions` stream declares incremental sync with
`updated_at` as the cursor, and that the correct `updated_after` query
parameter is injected into outgoing requests. See oncall issue
https://github.com/airbytehq/oncall/issues/12037 for context.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.types import StreamSlice


MANIFEST_PATH = str(Path(__file__).resolve().parents[1] / "manifest.yaml")
CONFIG: Mapping[str, Any] = {
    "api_token": "test-api-token",
    "org_id": "org_test",
    "start_date": "2024-01-01T00:00:00Z",
}

INCREMENTAL_STREAMS = ["sessions"]
FULL_REFRESH_ONLY_STREAMS = [
    "session_messages",
    "playbooks",
    "secrets",
    "knowledge_notes",
]


@pytest.fixture(scope="module")
def source() -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)


@pytest.fixture(scope="module")
def streams_by_name(source: YamlDeclarativeSource) -> Mapping[str, Any]:
    return {s.name: s for s in source.streams(config=CONFIG)}


@pytest.mark.parametrize("stream_name", INCREMENTAL_STREAMS)
def test_stream_declares_incremental_cursor(stream_name: str, streams_by_name: Mapping[str, Any]) -> None:
    stream = streams_by_name[stream_name]
    assert stream.cursor_field == "updated_at", (
        f"stream {stream_name} should be incremental with cursor_field=updated_at, got {stream.cursor_field!r}"
    )


@pytest.mark.parametrize("stream_name", FULL_REFRESH_ONLY_STREAMS)
def test_full_refresh_only_stream_has_no_cursor(stream_name: str, streams_by_name: Mapping[str, Any]) -> None:
    stream = streams_by_name[stream_name]
    assert not stream.cursor_field, f"stream {stream_name} should not declare a cursor_field but got {stream.cursor_field!r}"


def _get_retriever_and_slice(stream: Any) -> tuple[Any, StreamSlice]:
    partitions = list(stream.generate_partitions())
    assert partitions, f"expected at least one partition for stream {stream.name}"
    partition = partitions[0]
    retriever = partition._retriever
    slice_dict = partition.to_slice()
    stream_slice = StreamSlice(partition={}, cursor_slice=dict(slice_dict))
    return retriever, stream_slice


def test_sessions_initial_request_injects_updated_after(streams_by_name: Mapping[str, Any]) -> None:
    """Without prior state, the first request must include `updated_after` derived from `start_date`."""
    stream = streams_by_name["sessions"]
    retriever, stream_slice = _get_retriever_and_slice(stream)

    params = retriever._request_params(stream_slice=stream_slice, next_page_token=None)

    assert "updated_after" in params, f"expected `updated_after` in request params, got {params!r}"
    # 2024-01-01T00:00:00Z -> epoch seconds 1704067200
    assert str(params["updated_after"]) == "1704067200", (
        f"expected `updated_after`=1704067200 (2024-01-01T00:00:00Z), got {params['updated_after']!r}"
    )


def test_sessions_initial_request_defaults_to_epoch_zero_when_start_date_missing() -> None:
    """If `start_date` is omitted, the manifest falls back to epoch 0 so existing users are non-breaking."""
    config_without_start_date: Mapping[str, Any] = {
        "api_token": "test-api-token",
        "org_id": "org_test",
    }
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=config_without_start_date)
    streams = {s.name: s for s in source.streams(config=config_without_start_date)}
    stream = streams["sessions"]

    retriever, stream_slice = _get_retriever_and_slice(stream)

    params = retriever._request_params(stream_slice=stream_slice, next_page_token=None)

    assert "updated_after" in params
    assert str(params["updated_after"]) == "0", f"expected `updated_after`=0 when start_date missing, got {params['updated_after']!r}"


def test_sessions_slice_uses_epoch_seconds(streams_by_name: Mapping[str, Any]) -> None:
    """The DatetimeBasedCursor must emit slices with `%s` (epoch seconds) keys to match the API contract."""
    stream = streams_by_name["sessions"]
    partitions = list(stream.generate_partitions())
    assert partitions, "expected at least one partition for the sessions stream"
    slice_dict = partitions[0].to_slice()

    # 2024-01-01T00:00:00Z -> 1704067200
    assert slice_dict.get("start_time") == "1704067200", (
        f"expected start_time=1704067200 (epoch seconds for 2024-01-01T00:00:00Z), got {slice_dict!r}"
    )
