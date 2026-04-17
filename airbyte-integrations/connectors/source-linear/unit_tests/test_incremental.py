#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""Unit tests for source-linear incremental sync support.

These tests verify that the 12 eligible streams declare incremental sync and
inject the correct GraphQL variables (`filter.updatedAt.gte`, `orderBy`, `after`)
when combined with pagination and the `DatetimeBasedCursor`. See oncall issue
https://github.com/airbytehq/oncall/issues/11998 for context.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.types import StreamSlice


MANIFEST_PATH = str(Path(__file__).resolve().parents[1] / "manifest.yaml")
CONFIG: Mapping[str, Any] = {
    "api_key": "test-api-key",
    "start_date": "2024-01-01T00:00:00.000Z",
}

INCREMENTAL_STREAMS = [
    "issues",
    "customers",
    "users",
    "comments",
    "cycles",
    "customer_needs",
    "projects",
    "project_milestones",
    "issue_labels",
    "workflow_states",
    "teams",
    "attachments",
]

FULL_REFRESH_ONLY_STREAMS = [
    "project_statuses",
    "issue_relations",
    "customer_statuses",
    "customer_tiers",
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
    assert stream.cursor_field == "updatedAt", f"stream {stream_name} should be incremental with cursor_field=updatedAt"


@pytest.mark.parametrize("stream_name", FULL_REFRESH_ONLY_STREAMS)
def test_full_refresh_only_stream_has_no_cursor(stream_name: str, streams_by_name: Mapping[str, Any]) -> None:
    stream = streams_by_name[stream_name]
    assert not stream.cursor_field, f"stream {stream_name} should not declare a cursor_field but got {stream.cursor_field!r}"


def _build_full_request_body(
    stream: Any,
    *,
    next_page_token: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    """Compose the HTTP request body that the retriever sends on a single page.

    Mirrors the flow in `SimpleRetriever._fetch_next_page` -> `HttpRequester.send_request`:
    the retriever contributes paginator/cursor options via `extra_body_json`, and the
    requester merges those with its static `request_body_json` (the GraphQL query +
    hard-coded variables) using `combine_mappings(allow_same_value_merge=True)`.
    """
    partitions = list(stream.generate_partitions())
    assert partitions, f"expected at least one partition for stream {stream.name}"
    partition = partitions[0]
    retriever = partition._retriever
    slice_dict = partition.to_slice()
    stream_slice = StreamSlice(partition={}, cursor_slice=dict(slice_dict))

    extras = retriever._request_body_json(stream_slice=stream_slice, next_page_token=next_page_token)
    return retriever.requester._request_body_json(
        stream_state={},
        stream_slice=stream_slice,
        next_page_token=next_page_token,
        extra_body_json=extras,
    )


@pytest.mark.parametrize(
    "stream_name,graphql_field",
    [
        pytest.param("issues", "issues", id="issues"),
        pytest.param("comments", "comments", id="comments"),
        pytest.param("customer_needs", "customerNeeds", id="customer_needs"),
        pytest.param("project_milestones", "projectMilestones", id="project_milestones"),
    ],
)
def test_initial_request_body_has_updated_at_filter_and_order_by(
    stream_name: str,
    graphql_field: str,
    streams_by_name: Mapping[str, Any],
) -> None:
    """The first request must include `filter.updatedAt.gte` derived from `start_date` and `orderBy: updatedAt`."""
    body = _build_full_request_body(streams_by_name[stream_name], next_page_token=None)

    query = body["query"]
    assert f"{graphql_field}(after: $after, first:" in query
    assert "filter: $filter" in query
    assert "orderBy: $orderBy" in query

    variables = body["variables"]
    assert variables["orderBy"] == "updatedAt"
    assert variables["filter"]["updatedAt"]["gte"].startswith("2024-01-01T00:00:00")
    # Initial request: no pagination cursor yet.
    assert "after" not in variables


def test_paginated_request_body_includes_after_filter_and_order_by(
    streams_by_name: Mapping[str, Any],
) -> None:
    """On subsequent pages, `after` must merge with `filter` and `orderBy` under `variables`."""
    body = _build_full_request_body(
        streams_by_name["issues"],
        next_page_token={"next_page_token": "PAGE_CURSOR_TOKEN"},
    )
    variables = body["variables"]
    assert variables["after"] == "PAGE_CURSOR_TOKEN"
    assert variables["orderBy"] == "updatedAt"
    assert variables["filter"]["updatedAt"]["gte"].startswith("2024-01-01T00:00:00")


def test_users_stream_filters_but_does_not_order_by_updated_at(
    streams_by_name: Mapping[str, Any],
) -> None:
    """The Linear `users` query supports `filter` but not `orderBy: updatedAt`.

    Incremental still works because the cursor clamps records via `filter.updatedAt.gte`;
    ordering is just not guaranteed. We still emit `orderBy: updatedAt` in variables (the
    query field does pass `orderBy: $orderBy`), which Linear accepts as a no-op for the
    users query.
    """
    body = _build_full_request_body(streams_by_name["users"], next_page_token=None)
    variables = body["variables"]
    assert variables["filter"]["updatedAt"]["gte"].startswith("2024-01-01T00:00:00")
    assert variables["orderBy"] == "updatedAt"


def test_start_date_override_flows_into_filter(tmp_path: Path) -> None:
    """Changing `config.start_date` must change the `filter.updatedAt.gte` value."""
    custom_config = {"api_key": "test", "start_date": "2025-06-15T00:00:00.000Z"}
    src = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=custom_config)
    streams = {s.name: s for s in src.streams(config=custom_config)}
    body = _build_full_request_body(streams["issues"], next_page_token=None)
    assert body["variables"]["filter"]["updatedAt"]["gte"].startswith("2025-06-15T00:00:00")
