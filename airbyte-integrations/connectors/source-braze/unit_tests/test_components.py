#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition


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
