# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections import Counter

from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import (
    CONFIG,
    LIST_STREAMS,
    NOW,
    UNPAGINATED_STREAMS,
    fixture_record,
    list_request,
    page,
    search_request,
    unpaginated_page,
)
from mock_server.test_list_streams import stream_requests


@freeze_time(NOW)
def test_all_streams_in_one_read(record_property) -> None:
    streams = (*LIST_STREAMS, *UNPAGINATED_STREAMS, "issues", "issue_messages", "issue_threads", "knowledge_base_articles")
    catalog = CatalogBuilder()
    for stream in streams:
        catalog.with_stream(stream, SyncMode.full_refresh)
    issue = fixture_record("issues")
    knowledge_base = fixture_record("knowledge_bases")
    with HttpMocker() as mocker:
        for stream in LIST_STREAMS:
            for request in stream_requests(stream):
                mocker.get(request, page([fixture_record(stream)]))
        for stream in UNPAGINATED_STREAMS:
            for request in stream_requests(stream):
                mocker.get(request, unpaginated_page([fixture_record(stream)]))
        mocker.post(search_request(), page([issue]))
        for stream, path in (
            ("issue_messages", f"issues/{issue['id']}/messages"),
            ("issue_threads", f"issues/{issue['id']}/threads"),
            ("knowledge_base_articles", f"knowledge-bases/{knowledge_base['id']}/articles"),
        ):
            mocker.get(list_request(path), page([fixture_record(stream)]))
        output = read(get_source(CONFIG), config=CONFIG, catalog=catalog.build())
    counts = Counter(message.record.stream for message in output.records)
    terminal_statuses = {}
    print("\nstream | result | record count")
    for stream in streams:
        statuses = output.get_stream_statuses(stream)
        terminal_status = statuses[-1] if statuses else None
        terminal_statuses[stream] = terminal_status
        record_property(f"{stream}_terminal_status", terminal_status.value if terminal_status else "MISSING")
        result = "PASS" if counts[stream] and terminal_status == AirbyteStreamStatus.COMPLETE else "FAIL"
        print(f"{stream} | {result} | {counts[stream]}")
        record_property(stream, f"{result}: {counts[stream]} records")
    assert all(status == AirbyteStreamStatus.COMPLETE for status in terminal_statuses.values()), terminal_statuses
    assert output.errors == []
    assert set(counts) == set(streams)
    assert all(counts[stream] >= 1 for stream in streams)
