#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Mapping

import pytest
from airbyte_cdk.sources.file_based.file_types import JsonlParser


@pytest.mark.parametrize(
    "record, expected_schema",
    [
        pytest.param({}, {}, id="no_records"),
        pytest.param(
            {"col1": 1, "col2": 2.2, "col3": "3", "col4": ["a", "list"], "col5": {"inner": "obj"}, "col6": None, "col7": True},
            {
                "col1": {"type": "integer"},
                "col2": {"type": "number"},
                "col3": {"type": "string"},
                "col4": {"type": "array"},
                "col5": {"type": "object"},
                "col6": {"type": "null"},
                "col7": {"type": "boolean"},
            },
            id="all_columns_included_in_schema"
        ),
    ]
)
def test_type_mapping(record: Dict[str, Any], expected_schema: Mapping[str, str]) -> None:
    if expected_schema is None:
        with pytest.raises(ValueError):
            JsonlParser().infer_schema_for_record(record)
    else:
        assert JsonlParser.infer_schema_for_record(record) == expected_schema
