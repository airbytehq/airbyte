#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping, Optional, Union

import pytest as pytest
from airbyte_cdk.models import SyncMode

from airbyte_cdk.sources.declarative.stream_slicers.substream_slicer import ParentStreamConfig
from airbyte_cdk.sources.streams.core import Stream

from source_posthog.components import PosthogIncrementalSlicer, PosthogInterpolatedRequestOptionsProvider


parent_records = [{"id": 1, "data": "data1"}, {"id": 2, "data": "data2"}]
more_records = [{"id": 10, "data": "data10", "slice": "second_parent"}, {"id": 20, "data": "data20", "slice": "second_parent"}]

data_first_parent_slice = [{"id": 0, "slice": "first", "data": "A"}, {"id": 1, "slice": "first", "data": "B"}]
data_second_parent_slice = [{"id": 2, "slice": "second", "data": "C"}]
data_third_parent_slice = []
all_parent_data = data_first_parent_slice + data_second_parent_slice + data_third_parent_slice
parent_slices = [{"slice": "first"}, {"slice": "second"}, {"slice": "third"}]
second_parent_stream_slice = [{"slice": "second_parent"}]


class MockStream(Stream):
    def __init__(self, slices, records, name):
        self._slices = slices
        self._records = records
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "id"

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from self._slices

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        # The parent stream's records should always be read as full refresh
        assert sync_mode == SyncMode.full_refresh
        if not stream_slice:
            yield from self._records
        else:
            yield from [r for r in self._records if r["slice"] == stream_slice["slice"]]

state = {"2331": {"timestamp": "2021-12-10T10:21:35.003000+00:00"}}

@pytest.mark.parametrize(
    "test_name, stream_slice, last_record, expected_state",
    [
        ("test_update_cursor_no_state_no_record", {}, {}, {}),
        ("test_update_cursor_with_initial_state", state, {}, state),
        ("test_update_cursor_with_new_record", {"project_id": "2331"}, {"timestamp": "2021-12-10T10:21:35.003000+00:00"}, state),
        # ("test_update_cursor_with_state_single_parent", {"first_stream_id": "1234"}, {"timestamp": ""}, {"first_stream_id": "1234"}),
    ],
)
def test_update_cursor(test_name, stream_slice, last_record, expected_state):
    parent_stream_name_to_config = [
        ParentStreamConfig(
            stream=MockStream(parent_slices, data_first_parent_slice + data_second_parent_slice, "first_stream"),
            parent_key="id",
            stream_slice_field="project_id",
            options={},
        )
    ]

    slicer = PosthogIncrementalSlicer(parent_stream_configs=parent_stream_name_to_config, options={})
    slicer.update_cursor(stream_slice, last_record)
    updated_state = slicer.get_stream_state()
    assert updated_state == expected_state


config = {"start_date": "2020-01-01"}

@pytest.mark.parametrize(
    "test_name, stream_state, stream_slice, expected_request_params",
    [
        ("test_static_param", {}, {"project_id": "2331"}, {"after": "2020-01-01"}),
        ("test_static_param1", state, {"project_id": "2331"}, {'after': '2021-12-10T10:21:35.003000+00:00'}),
    ],
)
def test_interpolated_request_params(test_name, stream_state, stream_slice, expected_request_params):
    provider = PosthogInterpolatedRequestOptionsProvider(config=config, request_parameters={}, options={})

    actual_request_params = provider.get_request_params(stream_state=stream_state, stream_slice=stream_slice)

    assert actual_request_params == expected_request_params
