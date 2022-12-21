#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from source_braze import TransformToRecordComponent


def test_string_to_dict_transformation():
    """
    Test that given string record transforms to dict with given name and value as a record itself.
    """
    added_field = AddedFieldDefinition(
        path=["append_key"],
        value="{{ record }}",
        options={}
    )
    transformation = TransformToRecordComponent(fields=[added_field], options={})
    record = transformation.transform(record="StringRecord", config={}, stream_state={}, stream_slice={})
    expected_record = {"append_key": "StringRecord"}
    assert record == expected_record
