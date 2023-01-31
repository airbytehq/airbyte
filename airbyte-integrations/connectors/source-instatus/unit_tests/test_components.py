#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from source_instatus.components import ListAddFields, UpdatesSubstreamSlicer


@pytest.mark.parametrize(
    ["records", "stream_slices", "expected"],
    [pytest.param(
        [{'id': 'some id', 'updates_ids': ['some updates_id 1', 'some updates_id 2', 'some updates_id 3']}],
        [{'page_id': 'some page_id 1', 'parent_slice': {}}],
        [
            {
                'parent_stream_update_id': 'some updates_id 1', 'updates_object_id': 'some id',
                'parent_slice': {'page_id': 'some page_id 1', 'parent_slice': {}}
            },
            {
                'parent_stream_update_id': 'some updates_id 2', 'updates_object_id': 'some id',
                'parent_slice': {'page_id': 'some page_id 1', 'parent_slice': {}}
            },
            {
                'parent_stream_update_id': 'some updates_id 3', 'updates_object_id': 'some id',
                'parent_slice': {'page_id': 'some page_id 1', 'parent_slice': {}}
            }
        ]
    )]
)
def test_updates_substream_slicer(records, stream_slices, expected):
    parent_stream = MagicMock()
    parent_stream.stream.read_records = MagicMock(return_value=records)
    parent_stream.stream.stream_slices = MagicMock(return_value=stream_slices)
    parent_stream.parent_key = 'updates_ids'
    parent_stream.stream_slice_field = "parent_stream_update_id"
    slicer = UpdatesSubstreamSlicer(
        parent_stream_configs=[parent_stream],
        options={}
    )

    for stream_slice, expected_slice in zip(slicer.stream_slices(sync_mode=SyncMode.full_refresh, stream_state={}), expected):
        assert stream_slice == expected_slice


@pytest.mark.parametrize(
    ["input_record", "field", "kwargs", "expected"],
    [pytest.param(
        {'id': 'some id', 'updates': [{'id': 'some update id'}, {'id': 'some update id 2'}]},
        [(['updates_ids'], "{{ record['updates'] }}")],
        {},
        {'id': 'some id', 'updates': [{'id': 'some update id'}, {'id': 'some update id 2'}],
         'updates_ids': ['some update id', 'some update id 2']}
    )]
)
def test_list_add_fields_transformer(input_record, field, kwargs, expected):
    inputs = [AddedFieldDefinition(path=v[0], value=v[1], options={}) for v in field]
    assert ListAddFields(fields=inputs, options={"option": "test"}).transform(input_record, **kwargs) == expected
