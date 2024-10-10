#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.incremental import ChildPartitionResumableFullRefreshCursor, GlobalSubstreamCursor
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.types import Record, StreamSlice
from airbyte_cdk.sources.streams.core import StreamData


class MockStream(DeclarativeStream):

    def __init__(self, name: str, slices: List[StreamSlice], date_intervals_to_records: List[List[Record]]):
        self._slices = slices
        self._date_intervals_to_records = date_intervals_to_records
        # self._stream_cursor_field =
        self._name = name
        self._state = {}
        self._count = 0

    def read_only_records(self, state: Optional[Mapping[str, Any]] = None) -> Iterable[StreamData]:
        if state == {"updated_at": "2024-08-15"}:
            intervals = self._date_intervals_to_records[1:]
        else:
            intervals = self._date_intervals_to_records
        for records_for_date_interval in intervals:
            for record in records_for_date_interval:
                yield record

            # Technically this should happen in simple_retriever, but for the purposes of the unit_test we update state here
            self._state = {"updated_at": records_for_date_interval[0].data.get("updated_at")}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        self._state = value


def test_global_substream_cursor_with_rfr_cursor():
    date_intervals_to_records = [
        [
            Record(data={"id": "abc", "updated_at": "2024-07-15"}, associated_slice=StreamSlice(cursor_slice={"start": "2024-07-01", "end": "2024-07-31"}, partition={})),
            Record(data={"id": "def", "updated_at": "2024-07-15"}, associated_slice=StreamSlice(cursor_slice={"start": "2024-07-01", "end": "2024-07-31"}, partition={})),
        ],
        [Record(data={"id": "oof", "updated_at": "2024-08-15"}, associated_slice=StreamSlice(cursor_slice={"start": "2024-08-01", "end": "2024-08-31"}, partition={}))],
        [Record(data={"id": "buh", "updated_at": "2024-09-15"}, associated_slice=StreamSlice(cursor_slice={"start": "2024-09-01", "end": "2024-09-31"}, partition={}))],
    ]

    partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockStream(name="first_stream", slices=[], date_intervals_to_records=date_intervals_to_records),
                parent_key="id",
                partition_field="first_stream_id",
                incremental_dependency=True,
                parameters={},
                config={},
            )
        ],
        config={},
        parameters={}
    )

    cursor = GlobalSubstreamCursor(
        partition_router=partition_router,
        stream_cursor=ChildPartitionResumableFullRefreshCursor(parameters={}),
    )

    expected_slice_and_state = [
        (StreamSlice(partition={"first_stream_id": "abc", "parent_slice": {}}, cursor_slice={}), {'parent_state': {'first_stream': {}}, "state": {}}),
        (StreamSlice(partition={"first_stream_id": "def", "parent_slice": {}}, cursor_slice={}), {'parent_state': {'first_stream': {"updated_at": "2024-07-15"}}, "state": {}}),
        (StreamSlice(partition={"first_stream_id": "oof", "parent_slice": {}}, cursor_slice={}), {'parent_state': {'first_stream': {"updated_at": "2024-07-15"}}, "state": {}}),

        # This last slice may look odd, but the terminal value is a result of still using the RFR cursor which always ends the
        # final state message to indicate its successful completion
        (StreamSlice(partition={"first_stream_id": "buh", "parent_slice": {}}, cursor_slice={}), {'parent_state': {'first_stream': {"updated_at": "2024-09-15"}}, "state": {"__ab_full_refresh_sync_complete": True}, "lookback_window": 0}),
    ]

    i = 0
    for actual_slice in cursor.stream_slices():
        assert actual_slice == expected_slice_and_state[i][0]
        cursor.observe(stream_slice=actual_slice, record=Record(data={"id": "child_407"}, associated_slice=actual_slice))
        cursor.close_slice(actual_slice)
        actual_state = cursor.get_stream_state()
        assert actual_state == expected_slice_and_state[i][1]
        i += 1


def test_global_substream_cursor_with_rfr_cursor_with_state():
    date_intervals_to_records = [
        [
            Record(data={"id": "abc", "updated_at": "2024-07-15"},
                   associated_slice=StreamSlice(cursor_slice={"start": "2024-07-01", "end": "2024-07-31"}, partition={})),
            Record(data={"id": "def", "updated_at": "2024-07-15"},
                   associated_slice=StreamSlice(cursor_slice={"start": "2024-07-01", "end": "2024-07-31"}, partition={})),
        ],
        [Record(data={"id": "oof", "updated_at": "2024-08-15"},
                associated_slice=StreamSlice(cursor_slice={"start": "2024-08-01", "end": "2024-08-31"}, partition={}))],
        [Record(data={"id": "buh", "updated_at": "2024-09-15"},
                associated_slice=StreamSlice(cursor_slice={"start": "2024-09-01", "end": "2024-09-31"}, partition={}))],
    ]

    partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockStream(name="first_stream", slices=[], date_intervals_to_records=date_intervals_to_records),
                parent_key="id",
                partition_field="first_stream_id",
                incremental_dependency=True,
                parameters={},
                config={},
            )
        ],
        config={},
        parameters={}
    )

    cursor = GlobalSubstreamCursor(
        partition_router=partition_router,
        stream_cursor=ChildPartitionResumableFullRefreshCursor(parameters={}),
    )

    cursor.set_initial_state(
        {'parent_state': {'first_stream': {"updated_at": "2024-08-15"}}, "state": {}}
    )

    expected_slice_and_state = [
        (StreamSlice(partition={"first_stream_id": "oof", "parent_slice": {}}, cursor_slice={}),
         {'parent_state': {'first_stream': {"updated_at": "2024-08-15"}}, "state": {}}),

        # This last slice may look odd, but the terminal value is a result of still using the RFR cursor which always ends the
        # final state message to indicate its successful completion
        (StreamSlice(partition={"first_stream_id": "buh", "parent_slice": {}}, cursor_slice={}),
         {'parent_state': {'first_stream': {"updated_at": "2024-09-15"}}, "state": {"__ab_full_refresh_sync_complete": True},
          "lookback_window": 0}),
    ]

    i = 0
    for actual_slice in cursor.stream_slices():
        assert actual_slice == expected_slice_and_state[i][0]
        cursor.observe(stream_slice=actual_slice, record=Record(data={"id": "child_407"}, associated_slice=actual_slice))
        cursor.close_slice(actual_slice)
        actual_state = cursor.get_stream_state()
        assert actual_state == expected_slice_and_state[i][1]
        i += 1
