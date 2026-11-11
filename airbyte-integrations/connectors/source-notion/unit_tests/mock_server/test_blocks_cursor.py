# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock, patch

from airbyte_cdk.sources.declarative.extractors.record_filter import ClientSideIncrementalRecordFilterDecorator, RecordFilter
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import Record, StreamSlice


def test_selector_cursor_filter_is_moved_after_recursion(components_module):
    cursor = MagicMock()
    cursor.should_be_synced.side_effect = lambda record: record.data["id"] == "new-child"
    selector = MagicMock()
    selector.record_filter = ClientSideIncrementalRecordFilterDecorator(
        cursor=cursor, config={}, parameters={}, condition='{{ record["type"] != "child_page" }}'
    )
    retriever = components_module.BlocksRetriever(
        name="blocks",
        primary_key=["id"],
        requester=MagicMock(),
        record_selector=selector,
        config={},
        parameters={},
        client_side_incremental_sync={"cursor": cursor},
    )
    assert type(selector.record_filter) is RecordFilter
    visited = []

    def read_records(self, records_schema, stream_slice):
        block_id = stream_slice.partition["block_id"]
        visited.append(block_id)
        records = (
            [{"id": "old-parent", "has_children": True, "type": "paragraph"}, {"id": "excluded", "type": "child_page"}]
            if block_id == "page"
            else [{"id": "new-child", "type": "paragraph"}]
        )
        for data in selector.record_filter.filter_records(records, {}, stream_slice):
            yield Record(data=data, associated_slice=stream_slice, stream_name="blocks")

    with patch.object(SimpleRetriever, "read_records", read_records):
        records = list(retriever.read_records({}, StreamSlice(partition={"block_id": "page"}, cursor_slice={})))

    assert visited == ["page", "old-parent"]
    assert [record.data["id"] for record in records] == ["new-child"]
