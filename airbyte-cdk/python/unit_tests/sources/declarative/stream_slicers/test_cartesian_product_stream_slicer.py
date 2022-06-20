#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.stream_slicers.cartesian_product_stream_slicer import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer


@pytest.mark.parametrize(
    "test_name, stream_slicers, expected_slices",
    [
        (
            "test_single_stream_slicer",
            [ListStreamSlicer(["customer", "store", "subscription"], {"owner_resource": "{{ slice_value }}"}, None)],
            [{"owner_resource": "customer"}, {"owner_resource": "store"}, {"owner_resource": "subscription"}],
        ),
        (
            "test_two_stream_slicers",
            [
                ListStreamSlicer(["customer", "store", "subscription"], {"owner_resource": "{{ slice_value }}"}, None),
                ListStreamSlicer(["A", "B"], {"letter": "{{ slice_value }}"}, None),
            ],
            [
                {"owner_resource": "customer", "letter": "A"},
                {"owner_resource": "customer", "letter": "B"},
                {"owner_resource": "store", "letter": "A"},
                {"owner_resource": "store", "letter": "B"},
                {"owner_resource": "subscription", "letter": "A"},
                {"owner_resource": "subscription", "letter": "B"},
            ],
        ),
        (
            "test_list_and_datetime",
            [
                ListStreamSlicer(["customer", "store", "subscription"], {"owner_resource": "{{ slice_value }}"}, None),
                DatetimeStreamSlicer(
                    InterpolatedString("2021-01-01"), InterpolatedString("2021-01-03"), "1d", InterpolatedString(""), "%Y-%m-%d", None
                ),
            ],
            [
                {"owner_resource": "customer", "start_date": "2021-01-01", "end_date": "2021-01-01"},
                {"owner_resource": "customer", "start_date": "2021-01-02", "end_date": "2021-01-02"},
                {"owner_resource": "customer", "start_date": "2021-01-03", "end_date": "2021-01-03"},
                {"owner_resource": "store", "start_date": "2021-01-01", "end_date": "2021-01-01"},
                {"owner_resource": "store", "start_date": "2021-01-02", "end_date": "2021-01-02"},
                {"owner_resource": "store", "start_date": "2021-01-03", "end_date": "2021-01-03"},
                {"owner_resource": "subscription", "start_date": "2021-01-01", "end_date": "2021-01-01"},
                {"owner_resource": "subscription", "start_date": "2021-01-02", "end_date": "2021-01-02"},
                {"owner_resource": "subscription", "start_date": "2021-01-03", "end_date": "2021-01-03"},
            ],
        ),
    ],
)
def test_substream_slicer(test_name, stream_slicers, expected_slices):
    slicer = CartesianProductStreamSlicer(stream_slicers)
    slices = [s for s in slicer.stream_slices(SyncMode.incremental, stream_state=None)]
    assert slices == expected_slices
