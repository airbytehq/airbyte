#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from components import ListAddFields, UpdatesSubstreamPartitionRouter

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition


@pytest.mark.parametrize(
    ["records", "stream_slices", "expected"],
    [
        pytest.param(
            [{"id": "some id", "updates_ids": ["some updates_id 1", "some updates_id 2", "some updates_id 3"]}],
            [{"page_id": "some page_id 1", "parent_slice": {}}],
            [
                {
                    "parent_stream_update_id": "some updates_id 1",
                    "updates_object_id": "some id",
                    "parent_slice": {"page_id": "some page_id 1", "parent_slice": {}},
                },
                {
                    "parent_stream_update_id": "some updates_id 2",
                    "updates_object_id": "some id",
                    "parent_slice": {"page_id": "some page_id 1", "parent_slice": {}},
                },
                {
                    "parent_stream_update_id": "some updates_id 3",
                    "updates_object_id": "some id",
                    "parent_slice": {"page_id": "some page_id 1", "parent_slice": {}},
                },
            ],
        )
    ],
)
def test_updates_substream_partition_router(records, stream_slices, expected):
    parent_stream = MagicMock()
    parent_stream.stream.read_records = MagicMock(return_value=records)
    parent_stream.stream.stream_slices = MagicMock(return_value=stream_slices)
    parent_stream.parent_key = InterpolatedString(string="updates_ids", default="updates_ids", parameters={})
    parent_stream.partition_field = InterpolatedString(string="parent_stream_update_id", default="parent_stream_update_id", parameters={})
    slicer = UpdatesSubstreamPartitionRouter(parent_stream_configs=[parent_stream], parameters={}, config={})

    for stream_slice, expected_slice in zip(slicer.stream_slices(), expected):
        assert stream_slice == expected_slice


@pytest.mark.parametrize(
    ["input_record", "field", "kwargs", "expected"],
    [
        pytest.param(
            {"id": "some id", "updates": [{"id": "some update id"}, {"id": "some update id 2"}]},
            [(["updates_ids"], "{{ record['updates'] }}")],
            {},
            {
                "id": "some id",
                "updates": [{"id": "some update id"}, {"id": "some update id 2"}],
                "updates_ids": ["some update id", "some update id 2"],
            },
        )
    ],
)
def test_list_add_fields_transformer(input_record, field, kwargs, expected):
    inputs = [AddedFieldDefinition(path=v[0], value=v[1], value_type="string", parameters={}) for v in field]
    assert ListAddFields(fields=inputs, parameters={"parameter": "test"}).transform(input_record, **kwargs) == expected
