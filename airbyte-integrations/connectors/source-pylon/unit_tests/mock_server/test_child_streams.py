# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import NOW, fixture_record, list_request, page, run, search_request


CHILDREN = [
    ("issue_messages", "issues", "issue_id", "issues/{}/messages"),
    ("issue_threads", "issues", "issue_id", "issues/{}/threads"),
    ("knowledge_base_articles", "knowledge_bases", "knowledge_base_id", "knowledge-bases/{}/articles"),
]


@pytest.mark.parametrize("stream,parent,key,path", CHILDREN)
@freeze_time(NOW)
def test_child_parent_key(stream, parent, key, path):
    parent_record = fixture_record(parent)
    child = fixture_record(stream)
    child.pop(key, None)
    with HttpMocker() as mocker:
        parent_request = search_request() if parent == "issues" else list_request("knowledge-bases")
        register = mocker.post if parent == "issues" else mocker.get
        register(parent_request, page([parent_record]))
        child_request = list_request(path.format(parent_record["id"]))
        mocker.get(child_request, page([child]))
        output = run(stream)
        mocker.assert_number_of_calls(child_request, 1)
    assert output.errors == []
    assert len(output.records) == 1
    assert output.records[0].record.data.get(key) == parent_record["id"]


@pytest.mark.parametrize("stream,parent,key,path", CHILDREN)
@freeze_time(NOW)
def test_no_parents_means_no_child_requests(stream, parent, key, path):
    with HttpMocker() as mocker:
        request = search_request() if parent == "issues" else list_request("knowledge-bases")
        register = mocker.post if parent == "issues" else mocker.get
        register(request, page([]))
        output = run(stream)
        mocker.assert_number_of_calls(request, 1)
    assert output.errors == []
    assert output.records == []
