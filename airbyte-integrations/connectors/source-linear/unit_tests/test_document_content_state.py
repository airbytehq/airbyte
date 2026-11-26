# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""Tests for the move from Linear `[Internal]` fields to public GraphQL fields.

Linear SDK 102.0.0 removed `Issue.descriptionState`, `Project.contentState`,
`ProjectMilestone.descriptionState`, `CustomerNeed.bodyData` and `Team.joinByDefault`
from the public schema. The connector now reads the Yjs state from the public
`documentContent { contentState }` selection and writes it back to the old field name,
so the record shape stays the same. See https://github.com/airbytehq/oncall/issues/13982.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

import pytest
import yaml

from test_incremental_boundary import CONFIG, _catalog, _issue, _request, _response, _source, _stream_request_body

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker


MANIFEST_PATH = Path(__file__).resolve().parents[1] / "manifest.yaml"
YJS_STATE = "AT75ivCwBgAHAQtwcm9zZW1pcnJvcgMHaGVhZGluZwcA"

# Stream -> (GraphQL connection field, legacy output field filled from documentContent.contentState)
DOCUMENT_CONTENT_STREAMS: Mapping[str, tuple[str, str]] = {
    "issues": ("issues", "descriptionState"),
    "projects": ("projects", "contentState"),
    "project_milestones": ("projectMilestones", "descriptionState"),
}

# Stream -> fields that Linear removed from the public schema and that the query must not select.
REMOVED_FIELDS_BY_STREAM: Mapping[str, tuple[str, ...]] = {
    "issues": ("descriptionState",),
    "projects": ("contentState",),
    "project_milestones": ("descriptionState",),
    "customer_needs": ("bodyData",),
    "teams": ("joinByDefault",),
}


def _stream_definitions() -> Mapping[str, Mapping[str, Any]]:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    streams = dict(manifest["definitions"]["streams"])
    streams["issues"] = manifest["definitions"]["base_issues_stream"]
    return streams


def _query(stream_name: str) -> str:
    return _stream_definitions()[stream_name]["retriever"]["requester"]["request_body_json"]["query"]


def _node(stream_name: str, document_content: Any) -> Mapping[str, Any]:
    node_id = f"{stream_name}-1"
    updated_at = "2024-05-01T12:00:00.000Z"
    if stream_name == "issues":
        node: dict[str, Any] = dict(_issue(node_id, updated_at))
    elif stream_name == "projects":
        node = {
            "id": node_id,
            "updatedAt": updated_at,
            "convertedFromIssue": {"id": f"{node_id}-issue"},
            "creator": {"id": f"{node_id}-creator"},
            "lead": {"id": f"{node_id}-lead"},
            "status": {"id": f"{node_id}-status"},
            "teams": {"nodes": [{"id": f"{node_id}-team"}]},
        }
    else:
        node = {"id": node_id, "updatedAt": updated_at, "project": {"id": f"{node_id}-project"}}
    node["documentContent"] = document_content
    return node


def _read_one_record(stream_name: str, document_content: Any) -> Mapping[str, Any]:
    connection_field, _ = DOCUMENT_CONTENT_STREAMS[stream_name]
    with HttpMocker() as http_mocker:
        http_mocker.post(
            _request(_stream_request_body(stream_name)),
            _response(connection_field, [_node(stream_name, document_content)], has_next_page=False, end_cursor=None),
        )
        output = read(_source(), config=CONFIG, catalog=_catalog(stream_name, SyncMode.full_refresh))
    assert not output.errors, [error.trace.error.message for error in output.errors]
    assert len(output.records) == 1
    return output.records[0].record.data


@pytest.mark.parametrize("stream_name", sorted(REMOVED_FIELDS_BY_STREAM))
def test_query_does_not_select_fields_removed_from_public_schema(stream_name: str) -> None:
    # `contentState` stays valid inside the public `documentContent { ... }` selection.
    query = re.sub(r"documentContent\s*\{\s*contentState\s*\}", "", _query(stream_name))
    for field in REMOVED_FIELDS_BY_STREAM[stream_name]:
        assert not re.search(rf"\b{field}\b", query), f"{stream_name} still selects {field}"


@pytest.mark.parametrize("stream_name", sorted(DOCUMENT_CONTENT_STREAMS))
def test_query_selects_document_content_state(stream_name: str) -> None:
    assert re.search(r"documentContent\s*\{\s*contentState\s*\}", _query(stream_name))


# "1234" checks that `value_type: string` stops Jinja from casting a digit-only state to an integer.
@pytest.mark.parametrize("content_state", [YJS_STATE, "1234"], ids=["yjs_state", "digits_only"])
@pytest.mark.parametrize("stream_name", sorted(DOCUMENT_CONTENT_STREAMS))
def test_document_content_state_is_written_to_legacy_field(stream_name: str, content_state: str) -> None:
    _, legacy_field = DOCUMENT_CONTENT_STREAMS[stream_name]

    record = _read_one_record(stream_name, {"contentState": content_state})

    assert record[legacy_field] == content_state
    assert "documentContent" not in record


@pytest.mark.parametrize("document_content", [None, {"contentState": None}], ids=["no_document", "null_state"])
@pytest.mark.parametrize("stream_name", sorted(DOCUMENT_CONTENT_STREAMS))
def test_missing_document_content_leaves_legacy_field_empty(stream_name: str, document_content: Any) -> None:
    _, legacy_field = DOCUMENT_CONTENT_STREAMS[stream_name]

    record = _read_one_record(stream_name, document_content)

    assert record.get(legacy_field) is None
    assert "documentContent" not in record
