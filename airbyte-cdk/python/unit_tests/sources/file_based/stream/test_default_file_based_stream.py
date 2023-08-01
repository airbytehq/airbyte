#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.file_based.stream.default_file_based_stream import DefaultFileBasedStream


@pytest.mark.parametrize(
    "input_schema, expected_output",
    [
        pytest.param({}, {}, id="empty-schema"),
        pytest.param(
            {"type": "string"},
            {"type": ["null", "string"]},
            id="simple-schema",
        ),
        pytest.param(
            {"type": ["string"]},
            {"type": ["null", "string"]},
            id="simple-schema-list-type",
        ),
        pytest.param(
            {"type": ["null", "string"]},
            {"type": ["null", "string"]},
            id="simple-schema-already-has-null",
        ),
        pytest.param(
            {"properties": {"type": "string"}},
            {"properties": {"type": ["null", "string"]}},
            id="nested-schema",
        ),
        pytest.param(
            {"items": {"type": "string"}},
            {"items": {"type": ["null", "string"]}},
            id="array-schema",
        ),
        pytest.param(
            {"type": "object", "properties": {"prop": {"type": "string"}}},
            {"type": ["null", "object"], "properties": {"prop": {"type": ["null", "string"]}}},
            id="deeply-nested-schema",
        ),
    ],
)
def test_fill_nulls(input_schema: Mapping[str, Any], expected_output: Mapping[str, Any]) -> None:
    assert DefaultFileBasedStream._fill_nulls(input_schema) == expected_output
