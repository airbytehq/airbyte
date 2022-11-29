#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.schema import JsonFileSchemaLoader


@pytest.mark.parametrize(
    "test_name, input_path, expected_resource, expected_path",
    [
        ("path_prefixed_with_dot", "./source_example/schemas/lists.json", "source_example", "schemas/lists.json"),
        ("path_prefixed_with_slash", "/source_example/schemas/lists.json", "source_example", "schemas/lists.json"),
        ("path_starting_with_source", "source_example/schemas/lists.json", "source_example", "schemas/lists.json"),
        ("path_starting_missing_source", "schemas/lists.json", "schemas", "lists.json"),
        ("path_with_file_only", "lists.json", "", "lists.json"),
        ("empty_path_does_not_crash", "", "", ""),
        ("empty_path_with_slash_does_not_crash", "/", "", ""),
    ],
)
def test_extract_resource_and_schema_path(test_name, input_path, expected_resource, expected_path):
    json_schema = JsonFileSchemaLoader({}, {}, input_path)
    actual_resource, actual_path = json_schema.extract_resource_and_schema_path(input_path)

    assert actual_resource == expected_resource
    assert actual_path == expected_path


def test_recursive_schema():
    json_schema = JsonFileSchemaLoader(options={'name': 'sample_stream'},
                                       config={},
                                       file_path="source_test/schemas/{{options['name']}}.json")
    schema = json_schema.get_json_schema()
    joined_schema = {'$schema': 'http://json-schema.org/draft-07/schema#',
                     'type': ['null', 'object'],
                     'properties': {'type': {'type': ['null', 'object'],
                                             'properties': {'id_internal': {'type': ['null', 'integer']},
                                                            'name': {'type': ['null', 'string']}}},
                                    'id': {'type': ['null', 'string']}}}
    assert schema == joined_schema
