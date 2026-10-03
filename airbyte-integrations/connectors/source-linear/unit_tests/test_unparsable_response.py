# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Regression test: a 200 response with a truncated/unparsable body is retried, not fatal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import pytest

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


def _source() -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)


def _catalog(stream_name: str) -> Any:
    return CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()


def _stream_request_body(stream_name: str) -> Mapping[str, Any]:
    stream = {stream.name: stream for stream in _source().streams(config=CONFIG)}[stream_name]
    partition = next(iter(stream.generate_partitions()))
    retriever = partition._retriever
    stream_slice = StreamSlice(partition={}, cursor_slice=dict(partition.to_slice()))
    body = retriever.requester._request_body_json(
        stream_state={},
        stream_slice=stream_slice,
        next_page_token=None,
        extra_body_json=retriever._request_body_json(stream_slice=stream_slice, next_page_token=None),
    )
    body["variables"]["filter"] = {"updatedAt": {"gte": "2024-05-01T00:00:00.000000Z"}}
    return body


def _request(body: Mapping[str, Any]) -> HttpRequest:
    return HttpRequest(GRAPHQL_URL, body=body)


def _response(field: str, records: list[Mapping[str, Any]], *, has_next_page: bool, end_cursor: str | None) -> HttpResponse:
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


def _issue(issue_id: str) -> Mapping[str, Any]:
    return {
        "id": issue_id,
        "updatedAt": "2024-05-01T12:00:00.000Z",
        "assignee": {"id": f"{issue_id}-assignee"},
        "creator": {"id": f"{issue_id}-creator"},
        "cycle": {"id": f"{issue_id}-cycle"},
        "state": {"id": f"{issue_id}-state"},
        "team": {"id": f"{issue_id}-team"},
        "parent": {"id": f"{issue_id}-parent"},
        "project": {"id": f"{issue_id}-project"},
        "projectMilestone": {"id": f"{issue_id}-milestone"},
        "attachments": {"nodes": [{"id": f"{issue_id}-attachment"}]},
        "labels": {"nodes": [{"id": f"{issue_id}-label"}]},
        "subscribers": {"nodes": [{"id": f"{issue_id}-subscriber"}]},
        "relations": {"nodes": [{"id": f"{issue_id}-relation"}]},
        "sourceComment": {"id": f"{issue_id}-comment"},
    }


def test_issues_retries_truncated_json_body_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda *args: None)
    request = _request(_stream_request_body("issues"))
    with HttpMocker() as http_mocker:
        http_mocker.post(
            request,
            [
                HttpResponse(
                    body='{"data": {"issues": {"nodes": [{"id": "issue-1", "updatedAt": "2024-05-01T1',
                    status_code=200,
                ),
                _response("issues", [_issue("issue-1")], has_next_page=False, end_cursor=None),
            ],
        )

        output = read(_source(), config=CONFIG, catalog=_catalog("issues"))

        assert [message.record.data["id"] for message in output.records] == ["issue-1"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 2)
