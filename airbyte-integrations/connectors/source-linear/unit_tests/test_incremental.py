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

import re
from datetime import datetime, timedelta, timezone
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

# Stream name -> top-level GraphQL field name that must receive `filter` and `orderBy`.
INCREMENTAL_STREAM_GRAPHQL_FIELDS: Mapping[str, str] = {
    "issues": "issues",
    "customers": "customers",
    "users": "users",
    "comments": "comments",
    "cycles": "cycles",
    "customer_needs": "customerNeeds",
    "projects": "projects",
    "project_milestones": "projectMilestones",
    "issue_labels": "issueLabels",
    "workflow_states": "workflowStates",
    "teams": "teams",
    "attachments": "attachments",
}
INCREMENTAL_STREAMS = list(INCREMENTAL_STREAM_GRAPHQL_FIELDS)

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


def _top_level_call_site(query: str, graphql_field: str) -> str:
    """Return the argument list of the top-level GraphQL field call.

    A substring match against the full query is not sufficient because `filter: $filter`
    and `orderBy: $orderBy` also appear in the query's variable *declaration*. This helper
    isolates the first `<field>(...)` call site so assertions can target it directly.
    """
    match = re.search(rf"(?<![A-Za-z_]){re.escape(graphql_field)}\(([^)]*)\)", query)
    assert match, f"could not find top-level {graphql_field}(...) call in query: {query!r}"
    return match.group(1)


@pytest.mark.parametrize("stream_name", INCREMENTAL_STREAMS)
def test_initial_request_body_has_updated_at_filter_and_order_by(
    stream_name: str,
    streams_by_name: Mapping[str, Any],
) -> None:
    """The first request must pass `filter` and `orderBy` at the call site and inject `filter.updatedAt.gte`."""
    graphql_field = INCREMENTAL_STREAM_GRAPHQL_FIELDS[stream_name]
    body = _build_full_request_body(streams_by_name[stream_name], next_page_token=None)

    call_site = _top_level_call_site(body["query"], graphql_field)
    assert "filter: $filter" in call_site, f"{graphql_field} call site must pass filter: $filter, got: {call_site!r}"
    assert "orderBy: $orderBy" in call_site, f"{graphql_field} call site must pass orderBy: $orderBy, got: {call_site!r}"

    variables = body["variables"]
    assert variables["orderBy"] == "updatedAt"
    assert variables["filter"]["updatedAt"]["gte"].startswith("2024-01-01T00:00:00")
    # Initial request: no pagination cursor yet.
    assert "after" not in variables


@pytest.mark.parametrize("stream_name", INCREMENTAL_STREAMS)
def test_paginated_request_body_includes_after_filter_and_order_by(
    stream_name: str,
    streams_by_name: Mapping[str, Any],
) -> None:
    """On subsequent pages, `after` must merge with `filter` and `orderBy` at the call site and under `variables`."""
    graphql_field = INCREMENTAL_STREAM_GRAPHQL_FIELDS[stream_name]
    body = _build_full_request_body(
        streams_by_name[stream_name],
        next_page_token={"next_page_token": "PAGE_CURSOR_TOKEN"},
    )

    call_site = _top_level_call_site(body["query"], graphql_field)
    assert "after: $after" in call_site, f"{graphql_field} call site must pass after: $after, got: {call_site!r}"
    assert "filter: $filter" in call_site, f"{graphql_field} call site must pass filter: $filter, got: {call_site!r}"
    assert "orderBy: $orderBy" in call_site, f"{graphql_field} call site must pass orderBy: $orderBy, got: {call_site!r}"

    variables = body["variables"]
    assert variables["after"] == "PAGE_CURSOR_TOKEN"
    assert variables["orderBy"] == "updatedAt"
    assert variables["filter"]["updatedAt"]["gte"].startswith("2024-01-01T00:00:00")


def test_start_date_override_flows_into_filter(tmp_path: Path) -> None:
    """Changing `config.start_date` must change the `filter.updatedAt.gte` value."""
    custom_config = {"api_key": "test", "start_date": "2025-06-15T00:00:00.000Z"}
    src = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=custom_config)
    streams = {s.name: s for s in src.streams(config=custom_config)}
    body = _build_full_request_body(streams["issues"], next_page_token=None)
    assert body["variables"]["filter"]["updatedAt"]["gte"].startswith("2025-06-15T00:00:00")


def test_default_start_date_is_roughly_two_years_ago() -> None:
    """When `start_date` is not configured, the manifest falls back to `now_utc() - 2 years`.

    The fallback is rendered by Jinja at runtime, so assert the resulting datetime lands
    within a generous window around `today - 2 years` to avoid clock-skew flakiness.
    """
    config = {"api_key": "test"}
    src = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=config)
    streams = {s.name: s for s in src.streams(config=config)}
    body = _build_full_request_body(streams["issues"], next_page_token=None)

    gte = body["variables"]["filter"]["updatedAt"]["gte"]
    parsed = datetime.strptime(gte, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    expected = datetime.now(tz=timezone.utc) - timedelta(days=365 * 2)
    delta = abs((parsed - expected).total_seconds())
    # +/- 2 days tolerance for leap years and clock drift.
    assert delta < 2 * 24 * 3600, f"expected ~2 years ago, got {gte!r} (delta={delta}s)"


def test_flat_api_key_config_migrates_to_api_key_credentials() -> None:
    """Existing flat API key configs must keep using API key auth."""
    config = {"api_key": "test-api-key"}

    src = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=config)

    assert src._config["credentials"] == {
        "auth_type": "API Key",
        "api_key": "test-api-key",
    }


def test_flat_api_key_config_after_migration_can_build_auth_header() -> None:
    """The migrated API key must be available to CHECK stream requests."""
    config = {"api_key": "test-api-key"}

    src = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=config)
    streams = {s.name: s for s in src.streams(config=config)}
    stream = streams["issues"]
    partition = next(iter(stream.generate_partitions()))
    headers = partition._retriever.requester._request_headers()

    assert headers["Authorization"] == "test-api-key"
