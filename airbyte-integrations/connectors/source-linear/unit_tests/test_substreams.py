# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Test substream (parent/child) request construction for source-linear."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

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


def _missing_issue_history_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"data": {"issue": None}}))


def test_issue_history_reads_each_parent_with_exact_requests_and_paginates() -> None:
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)
    streams = {stream.name: stream for stream in source.streams(config=CONFIG)}
    child_stream = streams["issue_history"]
    parent_stream = child_stream._stream_partition_generator._partition_factory._retriever.request_option_provider.parent_stream_configs[
        0
    ].stream
    parent_body = _request_body(parent_stream)
    assert "filter" not in parent_body["variables"]
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
                [_issue("issue-1", "2024-04-15T00:00:00.000Z"), _issue("issue-2", "2024-05-01T02:00:00.000Z")],
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
    streams = {stream.name: stream for stream in source.streams(config=CONFIG)}
    child_stream = streams["issue_history"]
    parent_stream = child_stream._stream_partition_generator._partition_factory._retriever.request_option_provider.parent_stream_configs[
        0
    ].stream
    parent_request = _request(_request_body(parent_stream))
    child_request_1 = _request(_request_body(child_stream, partition={"issue_id": "issue-1"}))
    child_request_2 = _request(_request_body(child_stream, partition={"issue_id": "issue-2"}))

    with HttpMocker() as http_mocker:
        http_mocker.post(
            parent_request,
            _connection_response(
                "issues",
                [_issue("issue-1", "2024-04-15T00:00:00.000Z"), _issue("issue-2", "2024-05-01T02:00:00.000Z")],
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
    stream = {stream.name: stream for stream in source.streams(config=CONFIG)}["initiative_to_projects"]
    page_2_body = _request_body(stream, after="ITP-PAGE-2")
    assert page_2_body["variables"]["after"] == "ITP-PAGE-2", "paginator must inject variables.after"
    page_1 = _request(_request_body(stream))
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
