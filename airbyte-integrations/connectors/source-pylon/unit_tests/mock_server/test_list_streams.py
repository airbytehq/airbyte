# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import Status
from airbyte_cdk.test.entrypoint_wrapper import discover
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import CONFIG, LIST_STREAMS, NOW, check, fixture_record, list_request, page, run


def stream_requests(stream, cursor=None):
    path = stream.replace("_", "-")
    if stream == "custom_fields":
        return [list_request(path, cursor, object_type=kind) for kind in ("account", "issue", "contact")]
    return [list_request(path, cursor)]


@pytest.mark.parametrize("stream", LIST_STREAMS)
@pytest.mark.parametrize("empty", [False, True])
@freeze_time(NOW)
def test_list_streams(stream, empty):
    records = [] if empty else [fixture_record(stream)]
    requests = stream_requests(stream)
    with HttpMocker() as mocker:
        for request in requests:
            mocker.get(request, page(records))
        output = run(stream)
        for request in requests:
            mocker.assert_number_of_calls(request, 1)
    assert output.errors == []
    assert [message.record.data for message in output.records] == records * len(requests)


@pytest.mark.parametrize("stream", LIST_STREAMS)
@freeze_time(NOW)
def test_cursor_pagination(stream):
    first = fixture_record(stream)
    second = {**first, "name": "synthetic-second-page"}
    initial = stream_requests(stream)
    following = stream_requests(stream, "synthetic-cursor")
    with HttpMocker() as mocker:
        for request in initial:
            mocker.get(request, page([first], "synthetic-cursor"))
        for request in following:
            mocker.get(request, page([second]))
        output = run(stream)
        for request in initial + following:
            mocker.assert_number_of_calls(request, 1)
    assert output.errors == []
    actual = sorted(json.dumps(message.record.data, sort_keys=True) for message in output.records)
    expected = sorted(json.dumps(record, sort_keys=True) for record in [first, second] * len(initial))
    assert actual == expected


@freeze_time(NOW)
def test_check_and_discover():
    with HttpMocker() as mocker:
        request = list_request("tags")
        mocker.get(request, page([]))
        output = check()
        mocker.assert_number_of_calls(request, 1)
    assert output.connection_status_messages[0].connectionStatus.status == Status.SUCCEEDED
    catalog = discover(get_source(CONFIG), CONFIG).catalog.catalog
    assert {stream.name for stream in catalog.streams} == set(LIST_STREAMS) | {
        "issues",
        "issue_messages",
        "issue_threads",
        "knowledge_base_articles",
    }
