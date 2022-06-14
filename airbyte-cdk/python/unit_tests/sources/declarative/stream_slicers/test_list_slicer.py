#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer


@pytest.mark.parametrize(
    "test_name, slice_values, slice_definition, expected_slices",
    [
        (
            "test_single_element",
            ["customer", "store", "subscription"],
            {"owner_resource": "{{ slice_value }}"},
            [{"owner_resource": "customer"}, {"owner_resource": "store"}, {"owner_resource": "subscription"}],
        ),
    ],
)
def test_list_slicer(test_name, slice_values, slice_definition, expected_slices):
    slicer = ListStreamSlicer(slice_values, slice_definition, config={})
    slices = [s for s in slicer.stream_slices(SyncMode.incremental, stream_state=None)]
    assert slices == expected_slices
