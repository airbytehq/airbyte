#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import patch

import pytest
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader, _default_file_path


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


@patch("airbyte_cdk.sources.declarative.schema.json_file_schema_loader.sys")
def test_exclude_cdk_packages(mocked_sys):
    keys = ["airbyte_cdk.sources.concurrent_source.concurrent_source_adapter", "source_gitlab.utils"]
    mocked_sys.modules = {key: "" for key in keys}

    default_file_path = _default_file_path()

    assert "source_gitlab" in default_file_path
