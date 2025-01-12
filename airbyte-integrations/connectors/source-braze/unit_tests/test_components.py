#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_braze import DatetimeIncrementalSyncComponent

from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition


def test_datetime_slicer(components_module):
    """
    - `step` to be added to stream slices.
    - `step` value one more higher than actual difference in days between end/start dates
    - `step` value exactly equal to difference in days between end/start dates for first slice item
    - take into account if difference in days between end/start dates less than `step` argument for last record
    """
    DatetimeIncrementalSyncComponent = components_module.DatetimeIncrementalSyncComponent
    slicer = DatetimeIncrementalSyncComponent(
        start_datetime="2022-12-01",
        end_datetime="2022-12-08",
        step="P3D",
        cursor_field="time",
        datetime_format="%Y-%m-%d",
        cursor_granularity="P1D",
        config={},
        parameters={},
        step_option=RequestOption(field_name="step", inject_into=RequestOptionType.request_parameter, parameters={}),
    )
    expected_slices = [
        {"start_time": "2022-12-01", "end_time": "2022-12-03", "step": 2},
        {"start_time": "2022-12-04", "end_time": "2022-12-06", "step": 3},
        {"start_time": "2022-12-07", "end_time": "2022-12-08", "step": 2},
    ]
    assert slicer.stream_slices() == expected_slices


def test_string_to_dict_transformation(components_module):
    """
    Test that given string record transforms to dict with given name and value as a record itself.
    """
    TransformToRecordComponent = components_module.TransformToRecordComponent
    added_field = AddedFieldDefinition(value_type=str, path=["append_key"], value="{{ record }}", parameters={})
    transformation = TransformToRecordComponent(fields=[added_field], parameters={})
    record = transformation.transform(record="StringRecord", config={}, stream_state={}, stream_slice={})
    expected_record = {"append_key": "StringRecord"}
    assert record == expected_record
