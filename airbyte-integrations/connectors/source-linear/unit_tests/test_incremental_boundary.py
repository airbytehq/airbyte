# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Mapping

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


MANIFEST_PATH = str(Path(__file__).resolve().parents[1] / "manifest.yaml")
GRAPHQL_URL = "https://api.linear.app/graphql"
CONFIG: Mapping[str, Any] = {
    "api_key": "test-api-key",
    "start_date": "2024-05-01T00:00:00.000Z",
}
CURSOR = "2024-05-01T12:00:00.000Z"


def _normalize_cursor(cursor: str) -> str:
    return cursor.replace(".000Z", ".000000Z")


def _source(state: list[Any] | None = None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG, state=state)


def _catalog(stream_name: str, sync_mode: SyncMode) -> Any:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def _stream_request_body(
    stream_name: str,
    *,
    cursor: str | None = None,
    after: str | None = None,
    incremental: bool = True,
) -> Mapping[str, Any]:
    stream = {stream.name: stream for stream in _source().streams(config=CONFIG)}[stream_name]
    partition = next(iter(stream.generate_partitions()))
    retriever = partition._retriever
    stream_slice = StreamSlice(partition={}, cursor_slice=dict(partition.to_slice()))
    next_page_token = {"next_page_token": after} if after is not None else None
    body = retriever.requester._request_body_json(
        stream_state={},
        stream_slice=stream_slice,
        next_page_token=next_page_token,
        extra_body_json=retriever._request_body_json(
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        ),
    )
    if incremental:
        body["variables"]["filter"] = {"updatedAt": {"gte": _normalize_cursor(cursor or CONFIG["start_date"])}}
    else:
        body["variables"].pop("filter", None)
    if after is not None:
        body["variables"]["after"] = after
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


def _issue(issue_id: str, updated_at: str) -> Mapping[str, Any]:
    return {
        "id": issue_id,
        "updatedAt": updated_at,
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


def _user(user_id: str, updated_at: str) -> Mapping[str, Any]:
    return {
        "id": user_id,
        "updatedAt": updated_at,
        "teams": {"nodes": [{"id": f"{user_id}-team"}]},
    }


def _record_ids(output: EntrypointOutput) -> set[str]:
    return {message.record.data["id"] for message in output.records}


def _saved_state(output: EntrypointOutput) -> list[Any]:
    assert output.state_messages
    return [message.state for message in output.state_messages]


def _saved_cursor(output: EntrypointOutput) -> str:
    state = output.state_messages[-1].state.stream.stream_state
    return state.updatedAt


@pytest.mark.parametrize(
    ("stream_name", "graphql_field", "records"),
    [
        pytest.param(
            "issues",
            "issues",
            [
                _issue("issue-early", "2024-05-01T11:00:00.000Z"),
                _issue("issue-boundary", CURSOR),
            ],
            id="issues",
        ),
        pytest.param(
            "users",
            "users",
            [
                _user("user-early", "2024-05-01T11:00:00.000Z"),
                _user("user-boundary", CURSOR),
            ],
            id="users",
        ),
    ],
)
def test_incremental_syncs_are_inclusive_at_cursor_boundary(
    stream_name: str,
    graphql_field: str,
    records: list[Mapping[str, Any]],
) -> None:
    with HttpMocker() as http_mocker:
        first_page = records[:1] if stream_name == "issues" else records
        second_page = records[1:] if stream_name == "issues" else []
        http_mocker.post(
            _request(_stream_request_body(stream_name)),
            _response(
                graphql_field,
                first_page,
                has_next_page=bool(second_page),
                end_cursor="ISSUE_PAGE_2" if second_page else None,
            ),
        )
        if second_page:
            http_mocker.post(
                _request(_stream_request_body(stream_name, after="ISSUE_PAGE_2")),
                _response(graphql_field, second_page, has_next_page=False, end_cursor=None),
            )

        sync_one = read(_source(), config=CONFIG, catalog=_catalog(stream_name, SyncMode.incremental))
        saved_state = _saved_state(sync_one)
        saved_cursor = _saved_cursor(sync_one)
        assert saved_cursor == "2024-05-01T12:00:00.000000Z"

        http_mocker.post(
            _request(_stream_request_body(stream_name, cursor=saved_cursor)),
            _response(graphql_field, [records[-1]], has_next_page=False, end_cursor=None),
        )
        sync_two = read(
            _source(state=saved_state),
            config=CONFIG,
            catalog=_catalog(stream_name, SyncMode.incremental),
        )

        assert records[-1]["id"] in _record_ids(sync_one) | _record_ids(sync_two)
        assert _record_ids(sync_two) == {records[-1]["id"]}


def test_incremental_union_covers_full_refresh_for_paginated_issues() -> None:
    with HttpMocker() as http_mocker:
        records = [
            _issue("issue-early", "2024-05-01T11:00:00.000Z"),
            _issue("issue-boundary", CURSOR),
        ]
        http_mocker.post(
            _request(_stream_request_body("issues")),
            _response("issues", records[:1], has_next_page=True, end_cursor="ISSUE_PAGE_2"),
        )
        http_mocker.post(
            _request(_stream_request_body("issues", after="ISSUE_PAGE_2")),
            _response("issues", records[1:], has_next_page=False, end_cursor=None),
        )
        sync_one = read(_source(), config=CONFIG, catalog=_catalog("issues", SyncMode.incremental))

        http_mocker.post(
            _request(_stream_request_body("issues", incremental=False)),
            _response("issues", records, has_next_page=False, end_cursor=None),
        )
        full_refresh = read(_source(), config=CONFIG, catalog=_catalog("issues", SyncMode.full_refresh))

        http_mocker.post(
            _request(_stream_request_body("issues", cursor=_saved_cursor(sync_one))),
            _response("issues", [records[1]], has_next_page=False, end_cursor=None),
        )
        sync_two = read(
            _source(state=_saved_state(sync_one)),
            config=CONFIG,
            catalog=_catalog("issues", SyncMode.incremental),
        )

        assert _record_ids(full_refresh) == _record_ids(sync_one) | _record_ids(sync_two)


def test_failed_pagination_does_not_advance_cursor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time, "sleep", lambda _: None)
    with HttpMocker() as http_mocker:
        prior_cursor = "2024-05-01T10:00:00.000Z"
        state = StateBuilder().with_stream_state("issues", {"updatedAt": prior_cursor}).build()
        page_one_record = _issue("issue-before-failure", "2024-05-01T11:00:00.000Z")

        http_mocker.post(
            _request(_stream_request_body("issues", cursor=prior_cursor)),
            _response("issues", [page_one_record], has_next_page=True, end_cursor="FAILURE_PAGE_2"),
        )
        http_mocker.post(
            _request(_stream_request_body("issues", cursor=prior_cursor, after="FAILURE_PAGE_2")),
            [HttpResponse(body="{}", status_code=500) for _ in range(7)],
        )

        output = read(
            _source(state=state),
            config=CONFIG,
            catalog=_catalog("issues", SyncMode.incremental),
            expecting_exception=False,
        )

        assert output.errors
        assert output.state_messages
        assert _saved_cursor(output) == _normalize_cursor(prior_cursor)
