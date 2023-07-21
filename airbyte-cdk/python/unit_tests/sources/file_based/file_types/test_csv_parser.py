#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from airbyte_cdk.sources.file_based.file_types.csv_parser import cast_types

PROPERTY_TYPES = {
    "col1": "null",
    "col2": "boolean",
    "col3": "integer",
    "col4": "number",
    "col5": "string",
    "col6": "object",
    "col7": "array",
    "col8": "array",
    "col9": "array",
}

logger = logging.getLogger()


@pytest.mark.parametrize(
    "row,expected_output",
    [
        pytest.param(
            {
                "col1": "",
                "col2": "true",
                "col3": "1",
                "col4": "1.1",
                "col5": "asdf",
                "col6": '{"a": "b"}',
                "col7": '[1, 2]',
                "col8": '["1", "2"]',
                "col9": '[{"a": "b"}, {"a": "c"}]',
            }, {
                "col1": None,
                "col2": True,
                "col3": 1,
                "col4": 1.1,
                "col5": "asdf",
                "col6": {"a": "b"},
                "col7": [1, 2],
                "col8": ["1", "2"],
                "col9": [{"a": "b"}, {"a": "c"}],
            }, id="cast-all-cols"),
        pytest.param({"col1": "1"}, {"col1": "1"}, id="cannot-cast-to-null"),
        pytest.param({"col2": "1"}, {"col2": True}, id="cast-1-to-bool"),
        pytest.param({"col2": "0"}, {"col2": False}, id="cast-0-to-bool"),
        pytest.param({"col2": "yes"}, {"col2": True}, id="cast-yes-to-bool"),
        pytest.param({"col2": "no"}, {"col2": False}, id="cast-no-to-bool"),
        pytest.param({"col2": "10"}, {"col2": "10"}, id="cannot-cast-to-bool"),
        pytest.param({"col3": "1.1"}, {"col3": "1.1"}, id="cannot-cast-to-int"),
        pytest.param({"col4": "asdf"}, {"col4": "asdf"}, id="cannot-cast-to-float"),
        pytest.param({"col6": "{'a': 'b'}"}, {"col6": "{'a': 'b'}"}, id="cannot-cast-to-dict"),
        pytest.param({"col7": "['a', 'b']"}, {"col7": "['a', 'b']"}, id="cannot-cast-to-list-of-ints"),
        pytest.param({"col8": "['a', 'b']"}, {"col8": "['a', 'b']"}, id="cannot-cast-to-list-of-strings"),
        pytest.param({"col9": "['a', 'b']"}, {"col9": "['a', 'b']"}, id="cannot-cast-to-list-of-objects"),
        pytest.param({"col10": "x"}, {"col10": "x"}, id="item-not-in-props-doesn't-error"),
    ]
)
def test_cast_to_python_type(row, expected_output):
    assert cast_types(row, PROPERTY_TYPES, logger) == expected_output
