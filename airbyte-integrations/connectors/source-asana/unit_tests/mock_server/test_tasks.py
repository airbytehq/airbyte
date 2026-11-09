# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.mock_server.helpers import mock_parents, read_streams, request, response


def test_tasks_two_pages() -> None:
    with HttpMocker() as http:
        mock_parents(http, exclude="tasks")
        first, second = request("tasks"), request("tasks", offset="page-2")
        http.get(first, response("task-1", {"offset": "page-2"}))
        http.get(second, response("task-2"))
        output = read_streams("tasks")
        assert not output.errors
        assert len(output.records) == 2
        assert {r.record.data["gid"] for r in output.records} == {"task-1", "task-2"}
        http.assert_number_of_calls(first, 1)
        http.assert_number_of_calls(second, 1)


def test_child_reads_share_workspace_cache() -> None:
    with HttpMocker() as http:
        parents = mock_parents(http, exclude="tasks")
        http.get(request("tasks"), response("task-1"))
        output = read_streams("tasks", "tags")
        assert not output.errors
        assert {(r.record.stream, r.record.data["gid"]) for r in output.records} == {("tasks", "task-1"), ("tags", "1")}
        assert len(output.records) == 2
        http.assert_number_of_calls(parents["workspaces"], 1)
