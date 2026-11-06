# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import CONFIG, NOW, fixture_record, list_request, page, run, search_request


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


@freeze_time(NOW)
def test_many_parents_complete_with_two_workers(monkeypatch):
    pool_init = ThreadPoolManager.__init__
    enqueuer_init = PartitionEnqueuer.__init__
    prune = ThreadPoolManager.prune_to_validate_has_reached_futures_limit
    throttled = []

    def small_pending_limit(self, *args, **kwargs):
        kwargs["max_concurrent_tasks"] = 2
        pool_init(self, *args, **kwargs)

    def bounded_queue(self, *args, **kwargs):
        enqueuer_init(self, *args, **kwargs)
        self._queue.maxsize = 2

    def observe_throttling(self):
        reached_limit = prune(self)
        if reached_limit:
            throttled.append(True)
        return reached_limit

    monkeypatch.setattr(ThreadPoolManager, "__init__", small_pending_limit)
    monkeypatch.setattr(PartitionEnqueuer, "__init__", bounded_queue)
    monkeypatch.setattr(ThreadPoolManager, "prune_to_validate_has_reached_futures_limit", observe_throttling)
    parents = [{**fixture_record("knowledge_bases"), "id": f"synthetic-parent-{index}"} for index in range(16)]
    with HttpMocker() as mocker:
        mocker.get(list_request("knowledge-bases"), page(parents))
        for parent in parents:
            child = {**fixture_record("knowledge_base_articles"), "id": f"article-{parent['id']}"}
            mocker.get(list_request(f"knowledge-bases/{parent['id']}/articles"), page([child]))
        output = run("knowledge_base_articles", cfg={**CONFIG, "num_workers": 2})
    assert output.errors == []
    assert throttled
    assert len(output.records) == len(parents)
    assert {message.record.data["knowledge_base_id"] for message in output.records} == {parent["id"] for parent in parents}
    assert {message.record.data["id"] for message in output.records} == {f"article-{parent['id']}" for parent in parents}
