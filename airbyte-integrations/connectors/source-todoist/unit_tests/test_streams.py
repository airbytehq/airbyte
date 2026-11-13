# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `tasks` and `projects` streams on `source-todoist`.

Both streams read Todoist API v1 list endpoints (`GET /api/v1/tasks`,
`GET /api/v1/projects`), which return `{"results": [...], "next_cursor": ...}`
and paginate with the `cursor` and `limit` query parameters.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from unittest import TestCase

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_BASE_URL = "https://api.todoist.com/api/v1"
_TOKEN = "test-token"
_CONFIG = {"token": _TOKEN}
_PAGE_SIZE = 200


def _request(path: str, cursor: Optional[str] = None) -> HttpRequest:
    query_params: Dict[str, str] = {"limit": str(_PAGE_SIZE)}
    if cursor is not None:
        query_params["cursor"] = cursor
    return HttpRequest(url=f"{_BASE_URL}{path}", query_params=query_params, headers={"Authorization": f"Bearer {_TOKEN}"})


def _page(records: List[Dict[str, Any]], next_cursor: Optional[str] = None) -> HttpResponse:
    return HttpResponse(body=json.dumps({"results": records, "next_cursor": next_cursor}), status_code=200)


def _task(task_id: str, **overrides) -> Dict[str, Any]:
    record = {
        "id": task_id,
        "user_id": "2671355",
        "project_id": "6Jf8VQXxpwv56VQ7",
        "section_id": None,
        "parent_id": None,
        "added_by_uid": "2671355",
        "assigned_by_uid": None,
        "responsible_uid": None,
        "labels": ["Food"],
        "deadline": None,
        "duration": {"amount": 15, "unit": "minute"},
        "checked": False,
        "is_deleted": False,
        "added_at": "2025-08-10T12:00:00.000000Z",
        "completed_at": None,
        "updated_at": "2025-08-10T12:00:00.000000Z",
        "due": {"date": "2025-08-11", "string": "tomorrow", "lang": "en", "is_recurring": False},
        "priority": 1,
        "child_order": 1,
        "content": "Buy milk",
        "description": "",
        "note_count": 0,
    }
    record.update(overrides)
    return record


def _project(project_id: str, **overrides) -> Dict[str, Any]:
    record = {
        "id": project_id,
        "name": "Inbox",
        "description": "",
        "color": "charcoal",
        "parent_id": None,
        "child_order": 0,
        "is_collapsed": False,
        "is_favorite": False,
        "is_shared": False,
        "is_archived": False,
        "is_deleted": False,
        "inbox_project": True,
        "can_assign_tasks": False,
        "creator_uid": "2671355",
        "created_at": "2025-08-01T00:00:00Z",
        "updated_at": "2025-08-01T00:00:00Z",
        "view_style": "list",
    }
    record.update(overrides)
    return record


def _without_nulls(record: Dict[str, Any]) -> Dict[str, Any]:
    """Emitted records omit null-valued top-level fields, so compare against the non-null subset."""
    return {key: value for key, value in record.items() if value is not None}


def _read(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog, state=StateBuilder().build())


class TestTasks(TestCase):
    @HttpMocker()
    def test_reads_all_pages_following_next_cursor(self, http_mocker: HttpMocker):
        """`next_cursor` from one page is sent back as `cursor` until the API returns `next_cursor: null`."""
        first_page = _request("/tasks")
        second_page = _request("/tasks", cursor="cursor-2")
        third_page = _request("/tasks", cursor="cursor-3")
        http_mocker.get(first_page, _page([_task("task-1"), _task("task-2")], next_cursor="cursor-2"))
        http_mocker.get(second_page, _page([_task("task-3")], next_cursor="cursor-3"))
        http_mocker.get(third_page, _page([_task("task-4")]))

        output = _read("tasks")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["task-1", "task-2", "task-3", "task-4"]
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)
        http_mocker.assert_number_of_calls(third_page, 1)

    @HttpMocker()
    def test_record_keeps_api_v1_shape(self, http_mocker: HttpMocker):
        """Records are the API v1 objects from `results`, including the `duration` and `due` sub-objects."""
        http_mocker.get(_request("/tasks"), _page([_task("task-1", checked=True, completed_at="2025-08-12T08:00:00.000000Z")]))

        output = _read("tasks")

        assert output.errors == []
        assert output.records[0].record.data == _without_nulls(_task("task-1", checked=True, completed_at="2025-08-12T08:00:00.000000Z"))

    @HttpMocker()
    def test_empty_results_emits_no_records(self, http_mocker: HttpMocker):
        http_mocker.get(_request("/tasks"), _page([]))

        output = _read("tasks")

        assert output.errors == []
        assert output.records == []


class TestProjects(TestCase):
    @HttpMocker()
    def test_reads_all_pages_following_next_cursor(self, http_mocker: HttpMocker):
        first_page = _request("/projects")
        second_page = _request("/projects", cursor="cursor-2")
        http_mocker.get(first_page, _page([_project("project-1")], next_cursor="cursor-2"))
        http_mocker.get(second_page, _page([_project("project-2", name="Work", inbox_project=False)]))

        output = _read("projects")

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["project-1", "project-2"]
        assert output.records[1].record.data == _without_nulls(_project("project-2", name="Work", inbox_project=False))
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)


@pytest.mark.parametrize("stream_name", ["tasks", "projects"])
def test_discover_declares_full_refresh_stream_with_api_v1_schema(stream_name):
    catalog = get_source(config=_CONFIG).discover(logging.getLogger("airbyte"), _CONFIG)
    stream = {stream.name: stream for stream in catalog.streams}[stream_name]

    assert stream.supported_sync_modes == [SyncMode.full_refresh]
    assert "child_order" in stream.json_schema["properties"]
    assert "order" not in stream.json_schema["properties"]
