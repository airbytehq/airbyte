#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_chargebee.components import CustomFieldTransformation, IncrementalSingleSliceCursor


@pytest.mark.parametrize(
    "record, expected_record",
    [
        ({"pk": 1, "name": "example"}, {"pk": 1, "name": "example", "custom_fields": []}),
        (
            {"pk": 1, "name": "example", "cf_field1": "val1", "cf_field2": "val2"},
            {
                "pk": 1,
                "name": "example",
                "cf_field1": "val1",
                "cf_field2": "val2",
                "custom_fields": [{"name": "cf_field1", "value": "val1"}, {"name": "cf_field2", "value": "val2"}],
            },
        ),
    ],
    ids=["no_custom_field", "custom_field"],
)
def test_field_transformation(record, expected_record):
    transformer = CustomFieldTransformation()
    transformed_record = transformer.transform(record)
    assert transformed_record == expected_record

def test_slicer():
    date_time_dict = {"updated_at": 1662459010}
    slicer = IncrementalSingleSliceCursor(config={}, parameters={}, cursor_field="updated_at")
    slicer.close_slice(date_time_dict, date_time_dict)
    assert slicer.get_stream_state() == date_time_dict
    assert slicer.get_request_headers() == {}
    assert slicer.get_request_body_data() == {}
    assert slicer.get_request_body_json() == {}