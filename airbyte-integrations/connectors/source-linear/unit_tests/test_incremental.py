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

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
import yaml
from requests import Response
from test_incremental_boundary import _issue

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


MANIFEST_PATH = str(Path(__file__).resolve().parents[1] / "manifest.yaml")
CONFIG: Mapping[str, Any] = {
    "api_key": "test-api-key",
    "start_date": "2024-01-01T00:00:00.000Z",
}

DATE_ONLY_PROPERTIES_BY_STREAM = {
    "initiatives": {"targetDate"},
    "issue_history": {"fromDueDate", "toDueDate"},
}
DATETIME_FORMAT_STREAMS = {"initiatives", "initiative_to_projects", "issue_history", "project_updates"}

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
    "initiatives": "initiatives",
    "project_updates": "projectUpdates",
}
INCREMENTAL_STREAMS = list(INCREMENTAL_STREAM_GRAPHQL_FIELDS)

FULL_REFRESH_ONLY_STREAMS = [
    "project_statuses",
    "issue_relations",
    "customer_statuses",
    "customer_tiers",
    "initiative_to_projects",
    "issue_history",
]

STREAM_GRAPHQL_FIELDS: Mapping[str, str] = {
    **INCREMENTAL_STREAM_GRAPHQL_FIELDS,
    "project_statuses": "projectStatuses",
    "issue_relations": "issueRelations",
    "customer_statuses": "customerStatuses",
    "customer_tiers": "customerTiers",
    "initiative_to_projects": "initiativeToProjects",
    "issue_history": "history",
}


@pytest.fixture(scope="module")
def source() -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)


@pytest.fixture(scope="module")
def streams_by_name(source: YamlDeclarativeSource) -> Mapping[str, Any]:
    return {s.name: s for s in source.streams(config=CONFIG)}


@pytest.fixture(scope="module")
def manifest() -> Mapping[str, Any]:
    return yaml.safe_load(Path(MANIFEST_PATH).read_text())


@pytest.mark.parametrize("stream_name", INCREMENTAL_STREAMS)
def test_stream_declares_incremental_cursor(stream_name: str, streams_by_name: Mapping[str, Any]) -> None:
    stream = streams_by_name[stream_name]
    assert stream.cursor_field == "updatedAt", f"stream {stream_name} should be incremental with cursor_field=updatedAt"


@pytest.mark.parametrize("stream_name", FULL_REFRESH_ONLY_STREAMS)
def test_full_refresh_only_stream_has_no_cursor(stream_name: str, streams_by_name: Mapping[str, Any]) -> None:
    stream = streams_by_name[stream_name]
    assert not stream.cursor_field, f"stream {stream_name} should not declare a cursor_field but got {stream.cursor_field!r}"


@pytest.mark.parametrize("stream_name, graphql_field", STREAM_GRAPHQL_FIELDS.items())
def test_every_stream_query_includes_archived_records(
    stream_name: str,
    graphql_field: str,
    streams_by_name: Mapping[str, Any],
) -> None:
    body = _build_full_request_body(streams_by_name[stream_name], next_page_token=None)
    call_site = _top_level_call_site(body["query"], graphql_field)
    assert "includeArchived: true" in call_site


@pytest.mark.parametrize("stream_name", STREAM_GRAPHQL_FIELDS)
def test_every_stream_schema_declares_archived_at(stream_name: str, manifest: Mapping[str, Any]) -> None:
    archived_at = manifest["schemas"][stream_name]["properties"]["archivedAt"]
    assert set(archived_at["type"]) == {"null", "string"}
    assert archived_at["format"] == "date-time"


@pytest.mark.parametrize("stream_name", STREAM_GRAPHQL_FIELDS)
def test_stream_schema_date_formats(stream_name: str, manifest: Mapping[str, Any]) -> None:
    properties = manifest["schemas"][stream_name]["properties"]
    date_only = DATE_ONLY_PROPERTIES_BY_STREAM.get(stream_name, set())

    for property_name in date_only:
        assert properties[property_name]["format"] == "date"

    if stream_name in DATETIME_FORMAT_STREAMS:
        for property_name, property_schema in properties.items():
            if property_name.endswith("At") and property_name not in date_only:
                assert property_schema["format"] == "date-time"


def test_issue_history_parent_is_unfiltered_and_issues_remains_incremental(
    streams_by_name: Mapping[str, Any],
) -> None:
    child_stream = streams_by_name["issue_history"]
    parent_stream = child_stream._stream_partition_generator._partition_factory._retriever.request_option_provider.parent_stream_configs[
        0
    ].stream
    parent_body = _build_full_request_body(parent_stream, next_page_token=None)
    assert "filter" not in parent_body["variables"]

    issues = streams_by_name["issues"]
    issues_body = _build_full_request_body(issues, next_page_token=None)
    assert issues_body["variables"]["filter"]["updatedAt"]["gte"].startswith("2024-01-01T00:00:00")
    assert set(issues.as_airbyte_stream().supported_sync_modes) == {
        SyncMode.full_refresh,
        SyncMode.incremental,
    }


@pytest.mark.parametrize("stream_name", ["issues", "projects"])
def test_issues_and_projects_schemas_declare_trashed(stream_name: str, manifest: Mapping[str, Any]) -> None:
    trashed = manifest["schemas"][stream_name]["properties"]["trashed"]
    assert set(trashed["type"]) == {"boolean", "null"}


def _request(body: Mapping[str, Any]) -> HttpRequest:
    return HttpRequest("https://api.linear.app/graphql", body=body)


def _connection_response(
    field: str,
    records: list[Mapping[str, Any]],
    *,
    has_next_page: bool = False,
    end_cursor: str | None = None,
) -> HttpResponse:
    return HttpResponse(
        body=json.dumps(
            {
                "data": {
                    field: {
                        "nodes": records,
                        "pageInfo": {"hasNextPage": has_next_page, "endCursor": end_cursor},
                    }
                }
            }
        )
    )


def _history_response(
    records: list[Mapping[str, Any]],
    *,
    has_next_page: bool = False,
    end_cursor: str | None = None,
) -> HttpResponse:
    return HttpResponse(
        body=json.dumps(
            {
                "data": {
                    "issue": {
                        "history": {
                            "nodes": records,
                            "pageInfo": {"hasNextPage": has_next_page, "endCursor": end_cursor},
                        }
                    }
                }
            }
        )
    )


def _missing_issue_history_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"data": {"issue": None}}))


def test_issue_history_reads_each_parent_with_exact_requests_and_paginates() -> None:
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)
    streams_by_name = {stream.name: stream for stream in source.streams(config=CONFIG)}
    child_stream = streams_by_name["issue_history"]
    parent_stream = child_stream._stream_partition_generator._partition_factory._retriever.request_option_provider.parent_stream_configs[
        0
    ].stream
    parent_body = _build_full_request_body(parent_stream, next_page_token=None)
    assert "filter" not in parent_body["variables"]
    child_body_1 = _build_full_request_body(
        child_stream,
        partition={"issue_id": "issue-1"},
        next_page_token=None,
    )
    child_body_1_page_2 = _build_full_request_body(
        child_stream,
        partition={"issue_id": "issue-1"},
        next_page_token={"next_page_token": "HISTORY-PAGE-2"},
    )
    child_body_2 = _build_full_request_body(
        child_stream,
        partition={"issue_id": "issue-2"},
        next_page_token=None,
    )
    parent_request = _request(parent_body)
    child_request_1 = _request(child_body_1)
    child_request_1_page_2 = _request(child_body_1_page_2)
    child_request_2 = _request(child_body_2)

    with HttpMocker() as http_mocker:
        http_mocker.post(
            parent_request,
            _connection_response(
                "issues",
                [_issue("issue-1", "2023-12-15T00:00:00.000Z"), _issue("issue-2", "2024-05-01T02:00:00.000Z")],
            ),
        )
        http_mocker.post(
            child_request_1,
            _history_response([{"id": "history-1"}], has_next_page=True, end_cursor="HISTORY-PAGE-2"),
        )
        http_mocker.post(child_request_1_page_2, _history_response([{"id": "history-2"}]))
        http_mocker.post(child_request_2, _history_response([{"id": "history-3"}]))

        output = read(
            source,
            config=CONFIG,
            catalog=CatalogBuilder().with_stream("issue_history", SyncMode.full_refresh).build(),
        )

    records = {message.record.data["id"]: message.record.data for message in output.records}
    assert {record["issueId"] for record in records.values()} == {"issue-1", "issue-2"}
    assert records["history-1"]["issueId"] == "issue-1"
    assert records["history-2"]["issueId"] == "issue-1"
    assert records["history-3"]["issueId"] == "issue-2"
    for request in (parent_request, child_request_1, child_request_1_page_2, child_request_2):
        http_mocker.assert_number_of_calls(request, 1)


def test_issue_history_skips_missing_parent_issue() -> None:
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)
    streams_by_name = {stream.name: stream for stream in source.streams(config=CONFIG)}
    child_stream = streams_by_name["issue_history"]
    parent_stream = child_stream._stream_partition_generator._partition_factory._retriever.request_option_provider.parent_stream_configs[
        0
    ].stream
    parent_request = _request(_build_full_request_body(parent_stream, next_page_token=None))
    child_request_1 = _request(
        _build_full_request_body(
            child_stream,
            partition={"issue_id": "issue-1"},
            next_page_token=None,
        )
    )
    child_request_2 = _request(
        _build_full_request_body(
            child_stream,
            partition={"issue_id": "issue-2"},
            next_page_token=None,
        )
    )

    with HttpMocker() as http_mocker:
        http_mocker.post(
            parent_request,
            _connection_response(
                "issues",
                [_issue("issue-1", "2023-12-15T00:00:00.000Z"), _issue("issue-2", "2024-05-01T02:00:00.000Z")],
            ),
        )
        http_mocker.post(child_request_1, _history_response([{"id": "history-1"}]))
        http_mocker.post(child_request_2, _missing_issue_history_response())

        output = read(
            source,
            config=CONFIG,
            catalog=CatalogBuilder().with_stream("issue_history", SyncMode.full_refresh).build(),
        )

    records = {message.record.data["id"]: message.record.data for message in output.records}
    assert set(records) == {"history-1"}
    assert records["history-1"]["issueId"] == "issue-1"
    for request in (parent_request, child_request_1, child_request_2):
        http_mocker.assert_number_of_calls(request, 1)


def test_initiative_to_projects_flattens_join_keys_and_paginates() -> None:
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)
    streams_by_name = {stream.name: stream for stream in source.streams(config=CONFIG)}
    stream = streams_by_name["initiative_to_projects"]
    page_2_body = _build_full_request_body(
        stream,
        next_page_token={"next_page_token": "ITP-PAGE-2"},
    )
    assert page_2_body["variables"]["after"] == "ITP-PAGE-2", "paginator must inject variables.after"
    page_1 = _request(_build_full_request_body(stream, next_page_token=None))
    page_2 = _request(page_2_body)

    with HttpMocker() as http_mocker:
        http_mocker.post(
            page_1,
            _connection_response(
                "initiativeToProjects",
                [{"id": "link-1", "initiative": {"id": "initiative-1"}, "project": {"id": "project-1"}}],
                has_next_page=True,
                end_cursor="ITP-PAGE-2",
            ),
        )
        http_mocker.post(
            page_2,
            _connection_response(
                "initiativeToProjects",
                [{"id": "link-2", "initiative": {"id": "initiative-2"}, "project": {"id": "project-2"}}],
            ),
        )

        output = read(
            source,
            config=CONFIG,
            catalog=CatalogBuilder().with_stream("initiative_to_projects", SyncMode.full_refresh).build(),
        )

    records = {message.record.data["id"]: message.record.data for message in output.records}
    assert set(records) == {"link-1", "link-2"}
    assert records["link-1"]["initiativeId"] == "initiative-1"
    assert records["link-1"]["projectId"] == "project-1"
    assert records["link-2"]["initiativeId"] == "initiative-2"
    assert records["link-2"]["projectId"] == "project-2"
    for request in (page_1, page_2):
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        pytest.param(
            {
                "id": "initiative-1",
                "creator": {"id": "user-1"},
                "owner": {"id": "user-2"},
                "parentInitiative": {"id": "parent-1"},
            },
            {"creatorId": "user-1", "ownerId": "user-2", "parentInitiativeId": "parent-1"},
            id="relationships-present",
        ),
        pytest.param(
            {"id": "initiative-2", "creator": None, "owner": None, "parentInitiative": None},
            {"creatorId": None, "ownerId": None, "parentInitiativeId": None},
            id="relationships-null",
        ),
    ],
)
def test_initiatives_flatten_nullable_relationships(
    response: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)
    streams_by_name = {stream.name: stream for stream in source.streams(config=CONFIG)}
    stream = streams_by_name["initiatives"]
    request = _request(_build_full_request_body(stream, next_page_token=None))

    with HttpMocker() as http_mocker:
        http_mocker.post(request, _connection_response("initiatives", [response]))

        output = read(
            source=source,
            config=CONFIG,
            catalog=CatalogBuilder().with_stream("initiatives", SyncMode.full_refresh).build(),
        )

    assert len(output.records) == 1
    record = output.records[0].record.data
    assert {field: record.get(field) for field in expected} == expected
    if any(value is None for value in expected.values()):
        selector = next(iter(stream.generate_partitions()))._retriever.record_selector
        transformed = list(selector.filter_and_transform([response], {}, stream.get_json_schema()))
        assert len(transformed) == 1
        assert {field: transformed[0].data[field] for field in expected} == expected


def _build_full_request_body(
    stream: Any,
    *,
    partition: Mapping[str, Any] | None = None,
    next_page_token: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    """Compose the HTTP request body that the retriever sends on a single page.

    Mirrors the flow in `SimpleRetriever._fetch_next_page` -> `HttpRequester.send_request`:
    the retriever contributes paginator/cursor options via `extra_body_json`, and the
    requester merges those with its static `request_body_json` (the GraphQL query +
    hard-coded variables) using `combine_mappings(allow_same_value_merge=True)`.
    """
    if stream.name == "issue_history":
        retriever = stream._stream_partition_generator._partition_factory._retriever
        stream_slice = StreamSlice(partition=partition or {"issue_id": "test-issue"}, cursor_slice={})
    else:
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


@pytest.mark.parametrize(
    "status_code, response_json, expected_action, expected_error_message",
    [
        pytest.param(
            400,
            {
                "errors": [
                    {"message": "Rate limit exceeded. Only 2500 requests are allowed per 1 hour.", "extensions": {"code": "RATELIMITED"}}
                ]
            },
            ResponseAction.RATE_LIMITED,
            "Rate limit exceeded for Linear API.",
            id="graphql_ratelimited_error",
        ),
        pytest.param(
            400,
            {"errors": [{"message": "Invalid input.", "extensions": {"code": "BAD_USER_INPUT"}}]},
            ResponseAction.FAIL,
            "Linear returned an error: Invalid input.",
            id="graphql_generic_error",
        ),
    ],
)
def test_graphql_error_handler_response_action(
    streams_by_name: Mapping[str, Any],
    status_code: int,
    response_json: Mapping[str, Any],
    expected_action: ResponseAction,
    expected_error_message: str,
) -> None:
    stream = streams_by_name["issues"]
    retriever = next(iter(stream.generate_partitions()))._retriever
    response = MagicMock(spec=Response, status_code=status_code)
    response.ok = status_code == 200
    response.headers = {"Content-Type": "application/json", "X-RateLimit-Requests-Reset": "1600000060000"}
    response.json.return_value = response_json

    result = retriever.requester.error_handler.interpret_response(response)

    assert result.response_action == expected_action
    assert result.error_message == expected_error_message
