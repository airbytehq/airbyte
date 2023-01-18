#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from source_airtable.schema_helpers import SchemaHelpers


def test_clean_name(field_name_to_cleaned, expected_clean_name):
    assert expected_clean_name == SchemaHelpers.clean_name(field_name_to_cleaned)


def test_get_json_schema(json_response, expected_json_schema):
    json_schema = SchemaHelpers.get_json_schema(json_response["records"][0])
    assert json_schema == expected_json_schema


def test_get_airbyte_stream(table, expected_json_schema):
    stream = SchemaHelpers.get_airbyte_stream(table, expected_json_schema)
    assert stream
    assert stream.name == table
    assert stream.json_schema == expected_json_schema
