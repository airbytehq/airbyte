#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition


def test_datetime_slicer(components_module):
    """
    Test that the component correctly:
    - Slices the time range into appropriate windows
    - Calculates length as the number of days in each window
    - Injects length parameter into request options
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
        step_option=RequestOption(field_name="length", inject_into=RequestOptionType.request_parameter, parameters={}),
    )

    slices = slicer.stream_slices()
    
    # Test the time windows are correct
    expected_slices = [
        {"start_time": "2022-12-01", "end_time": "2022-12-03"},
        {"start_time": "2022-12-04", "end_time": "2022-12-06"},
        {"start_time": "2022-12-07", "end_time": "2022-12-08"}
    ]
    assert slices == expected_slices

    # Test that length is calculated correctly for each slice
    for slice in slices:
        options = slicer._get_request_options(RequestOptionType.request_parameter, slice)
        # Length should be the number of days between start and end dates
        start_date = datetime.strptime(slice["start_time"], "%Y-%m-%d")
        end_date = datetime.strptime(slice["end_time"], "%Y-%m-%d")
        expected_length = (end_date - start_date).days + 1  # +1 because both start and end dates are inclusive
        assert options["length"] == expected_length


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
