#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock, Mock

import pytest
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.streams import Stream
from source_monday.components import IncrementalSingleSlice, IncrementalSubstreamSlicer


def test_slicer():
    date_time_dict = {"updated_at": "2022-09-05T10:10:10Z"}
    slicer = IncrementalSingleSlice(config={}, parameters={}, cursor_field="updated_at")
    slicer.close_slice(date_time_dict, date_time_dict)
    assert slicer.get_stream_state() == date_time_dict
    assert slicer.get_request_headers() == {}
    assert slicer.get_request_body_data() == {}
    assert slicer.get_request_body_json() == {}


@pytest.mark.parametrize(
    "last_record, expected, records",
    [
        (
                {"first_stream_cursor": "2022-09-06T10:10:10Z"},
                {'parent_stream_name': {'parent_cursor_field': 1662459010}, 'first_stream_cursor': '2022-09-06T10:10:10Z'},
                [{"first_stream_cursor": "2022-09-05T10:10:10Z"}],
        ),
        (None, {}, []),
    ],
)
def test_sub_slicer(last_record, expected, records):
    parent_stream = Mock(spec=Stream)
    parent_stream.name = "parent_stream_name"
    parent_stream.cursor_field = "parent_cursor_field"
    parent_stream.stream_slices.return_value = [{"a slice": "value"}]
    parent_stream.read_records = MagicMock(return_value=records)

    parent_config = ParentStreamConfig(
        stream=parent_stream,
        parent_key="id",
        partition_field="first_stream_id",
        parameters={},
        config={},
    )

    slicer = IncrementalSubstreamSlicer(
        config={}, parameters={}, cursor_field="first_stream_cursor", parent_stream_configs=[parent_config]
    )
    stream_slice = next(slicer.stream_slices()) if records else {}
    slicer.close_slice(stream_slice, last_record)
    assert slicer.get_stream_state() == expected
