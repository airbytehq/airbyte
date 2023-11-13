#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.schema import InlineSchemaLoader


@pytest.mark.parametrize(
    "test_name, input_schema, expected_schema",
    [
        ("schema", {"k": "string"}, {"k": "string"}),
        ("empty_schema", {}, {}),
    ],
)
def test_static_schema_loads(test_name, input_schema, expected_schema):
    schema_loader = InlineSchemaLoader(input_schema, {})

    assert schema_loader.get_json_schema() == expected_schema
