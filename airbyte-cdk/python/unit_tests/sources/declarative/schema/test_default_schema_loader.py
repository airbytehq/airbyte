#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.schema import DefaultSchemaLoader


@pytest.mark.parametrize(
    "found_schema, found_error, expected_schema",
    [
        pytest.param(
            {"type": "object", "properties": {}}, None, {"type": "object", "properties": {}}, id="test_has_schema_in_default_location"
        ),
        pytest.param(None, FileNotFoundError, {}, id="test_schema_file_does_not_exist"),
    ],
)
def test_get_json_schema(found_schema, found_error, expected_schema):
    default_schema_loader = DefaultSchemaLoader({}, {})

    json_file_schema_loader = MagicMock()
    if found_schema:
        json_file_schema_loader.get_json_schema.return_value = {"type": "object", "properties": {}}
    if found_error:
        json_file_schema_loader.get_json_schema.side_effect = found_error

    default_schema_loader.default_loader = json_file_schema_loader

    actual_schema = default_schema_loader.get_json_schema()
    assert actual_schema == expected_schema
