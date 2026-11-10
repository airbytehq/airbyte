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
    last_page,
    list_request,
    page,
    search_request,
    unpaginated_page,
    unpaginated_request,
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
                response = last_page([fixture_record(stream)]) if stream == "audit_logs" else page([fixture_record(stream)])
                mocker.get(request, response)
        for stream in UNPAGINATED_STREAMS:
            mocker.get(unpaginated_request(stream.replace("_", "-")), unpaginated_page([fixture_record(stream)]))
        mocker.post(search_request(), page([issue]))
        for stream, path in (
            ("issue_messages", f"issues/{issue['id']}/messages"),
            ("issue_threads", f"issues/{issue['id']}/threads"),
            ("knowledge_base_articles", f"knowledge-bases/{knowledge_base['id']}/articles"),
        ):
            mocker.get(list_request(path), page([fixture_record(stream)]))
        output = read(get_source(CONFIG), config=CONFIG, catalog=catalog.build())
    counts = Counter(message.record.stream for message in output.records)
    print("\nstream | result | record count")
    for stream in streams:
        statuses = output.get_stream_statuses(stream)
        assert statuses[-1] == AirbyteStreamStatus.COMPLETE
        record_property(f"{stream}_terminal_status", statuses[-1].value)
        result = "PASS" if counts[stream] else "FAIL"
        print(f"{stream} | {result} | {counts[stream]}")
        record_property(stream, f"{result}: {counts[stream]} records")
    assert output.errors == []
    assert set(counts) == set(streams)
    assert all(counts[stream] >= 1 for stream in streams)
