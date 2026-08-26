# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import pytest
import yaml
from test_incremental_boundary import _issue

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


MANIFEST_PATH = str(Path(__file__).resolve().parents[1] / "manifest.yaml")
GRAPHQL_URL = "https://api.linear.app/graphql"
CONFIG: Mapping[str, Any] = {
    "api_key": "test-api-key",
    "start_date": "2024-05-01T00:00:00.000Z",
}
NEW_STREAMS = {
    "initiatives": ["id"],
    "initiative_to_projects": ["id"],
    "project_updates": ["id"],
    "issue_history": ["issue_id", "id"],
}


@pytest.fixture(scope="module")
def source() -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)


@pytest.fixture(scope="module")
def streams_by_name(source: YamlDeclarativeSource) -> Mapping[str, Any]:
    return {stream.name: stream for stream in source.streams(config=CONFIG)}


@pytest.fixture(scope="module")
def manifest() -> Mapping[str, Any]:
    return yaml.safe_load(Path(MANIFEST_PATH).read_text())


def _request_body(
    stream: Any,
    *,
    partition: Mapping[str, Any] | None = None,
    after: str | None = None,
) -> Mapping[str, Any]:
    retriever = stream._stream_partition_generator._partition_factory._retriever
    if partition is None:
        generated_partition = next(iter(stream.generate_partitions()))
        retriever = generated_partition._retriever
        partition = generated_partition.to_slice()
    stream_slice = StreamSlice(partition=dict(partition), cursor_slice={})
    next_page_token = {"next_page_token": after} if after is not None else None
    extra_body_json = retriever._request_body_json(
        stream_slice=stream_slice,
        next_page_token=next_page_token,
    )
    return retriever.requester._request_body_json(
        stream_state={},
        stream_slice=stream_slice,
        next_page_token=next_page_token,
        extra_body_json=extra_body_json,
    )


def _request(body: Mapping[str, Any]) -> HttpRequest:
    return HttpRequest(GRAPHQL_URL, body=body)


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


@pytest.mark.parametrize("stream_name, primary_key", NEW_STREAMS.items())
def test_new_streams_exist_with_expected_primary_keys(
    streams_by_name: Mapping[str, Any],
    stream_name: str,
    primary_key: list[str],
) -> None:
    assert stream_name in streams_by_name
    assert streams_by_name[stream_name]._primary_key == primary_key


@pytest.mark.parametrize("stream_name", ["initiatives", "project_updates"])
def test_incremental_new_streams_inject_updated_at_filter(
    streams_by_name: Mapping[str, Any],
    stream_name: str,
) -> None:
    stream = streams_by_name[stream_name]
    body = _request_body(stream)

    assert stream.cursor_field == "updatedAt"
    assert body["variables"]["filter"]["updatedAt"]["gte"].startswith("2024-05-01T00:00:00")


def test_full_refresh_new_streams_have_no_incremental_cursor(streams_by_name: Mapping[str, Any]) -> None:
    assert not streams_by_name["initiative_to_projects"].cursor_field
    assert not streams_by_name["issue_history"].cursor_field


@pytest.mark.parametrize(
    "stream_name",
    ["initiatives", "initiative_to_projects", "project_updates", "issue_history"],
)
def test_new_stream_queries_include_archived_records(
    streams_by_name: Mapping[str, Any],
    stream_name: str,
) -> None:
    stream = streams_by_name[stream_name]
    body = _request_body(stream, partition={"issue_id": "test-issue"} if stream_name == "issue_history" else None)

    assert "includeArchived: true" in body["query"]


@pytest.mark.parametrize(
    ("stream_name", "date_fields", "datetime_fields"),
    [
        pytest.param(
            "initiatives",
            ["targetDate"],
            ["archivedAt", "canceledAt", "completedAt", "createdAt", "healthUpdatedAt", "startedAt", "updatedAt"],
            id="initiatives",
        ),
        pytest.param(
            "initiative_to_projects",
            [],
            ["archivedAt", "createdAt", "updatedAt"],
            id="initiative_to_projects",
        ),
        pytest.param(
            "project_updates",
            [],
            ["archivedAt", "createdAt", "editedAt", "updatedAt"],
            id="project_updates",
        ),
        pytest.param(
            "issue_history",
            ["fromDueDate", "toDueDate"],
            ["archivedAt", "createdAt", "updatedAt"],
            id="issue_history",
        ),
    ],
)
def test_new_stream_date_formats(
    manifest: Mapping[str, Any],
    stream_name: str,
    date_fields: list[str],
    datetime_fields: list[str],
) -> None:
    properties = manifest["schemas"][stream_name]["properties"]
    for field in date_fields:
        assert properties[field]["format"] == "date"
    for field in datetime_fields:
        assert properties[field]["format"] == "date-time"


@pytest.mark.parametrize(
    ("stream_name", "response", "expected"),
    [
        pytest.param(
            "initiatives",
            {
                "id": "initiative-1",
                "creator": {"id": "user-1"},
                "owner": {"id": "user-2"},
            },
            {"id": "initiative-1", "creatorId": "user-1", "ownerId": "user-2"},
            id="initiatives",
        ),
        pytest.param(
            "project_updates",
            {
                "id": "update-1",
                "project": {"id": "project-1"},
                "user": {"id": "user-3"},
            },
            {"id": "update-1", "projectId": "project-1", "userId": "user-3"},
            id="project_updates",
        ),
    ],
)
def test_new_stream_flattening_transformations(
    streams_by_name: Mapping[str, Any],
    stream_name: str,
    response: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    graphql_field = "initiatives" if stream_name == "initiatives" else "projectUpdates"
    body = _request_body(streams_by_name[stream_name])
    with HttpMocker() as http_mocker:
        http_mocker.post(_request(body), _connection_response(graphql_field, [response]))

        output = read(
            YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG),
            config=CONFIG,
            catalog=CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build(),
        )

    assert len(output.records) == 1
    record = output.records[0].record.data
    assert {field: record[field] for field in expected} == expected


def test_issue_history_reads_each_parent_with_exact_requests_and_paginates() -> None:
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)
    streams = {stream.name: stream for stream in source.streams(config=CONFIG)}
    parent_body = _request_body(streams["issues"])
    child_stream = streams["issue_history"]
    child_body_1 = _request_body(child_stream, partition={"issue_id": "issue-1"})
    child_body_1_page_2 = _request_body(child_stream, partition={"issue_id": "issue-1"}, after="HISTORY-PAGE-2")
    child_body_2 = _request_body(child_stream, partition={"issue_id": "issue-2"})
    parent_request = _request(parent_body)
    child_request_1 = _request(child_body_1)
    child_request_1_page_2 = _request(child_body_1_page_2)
    child_request_2 = _request(child_body_2)

    with HttpMocker() as http_mocker:
        http_mocker.post(
            parent_request,
            _connection_response(
                "issues",
                [_issue("issue-1", "2024-05-01T01:00:00.000Z"), _issue("issue-2", "2024-05-01T02:00:00.000Z")],
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
    assert {record["issue_id"] for record in records.values()} == {"issue-1", "issue-2"}
    assert records["history-1"]["issue_id"] == "issue-1"
    assert records["history-2"]["issue_id"] == "issue-1"
    assert records["history-3"]["issue_id"] == "issue-2"
    for request in (parent_request, child_request_1, child_request_1_page_2, child_request_2):
        http_mocker.assert_number_of_calls(request, 1)
