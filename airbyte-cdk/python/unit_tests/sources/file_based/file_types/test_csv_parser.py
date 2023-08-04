#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock, Mock

import pytest
from airbyte_cdk.sources.file_based.config.csv_format import DEFAULT_FALSE_VALUES, DEFAULT_TRUE_VALUES, CsvFormat
from airbyte_cdk.sources.file_based.exceptions import RecordParseError
from airbyte_cdk.sources.file_based.file_types.csv_parser import CsvParser, _cast_types

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
    "row, true_values, false_values, expected_output",
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
            },
            DEFAULT_TRUE_VALUES,
            DEFAULT_FALSE_VALUES,
            {
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
        pytest.param({"col1": "1"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col1": "1"}, id="cannot-cast-to-null"),
        pytest.param({"col2": "1"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col2": True}, id="cast-1-to-bool"),
        pytest.param({"col2": "0"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col2": False}, id="cast-0-to-bool"),
        pytest.param({"col2": "yes"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col2": True}, id="cast-yes-to-bool"),
        pytest.param({"col2": "this_is_a_true_value"}, ["this_is_a_true_value"], DEFAULT_FALSE_VALUES, {"col2": True}, id="cast-custom-true-value-to-bool"),
        pytest.param({"col2": "this_is_a_false_value"}, DEFAULT_TRUE_VALUES, ["this_is_a_false_value"], {"col2": False}, id="cast-custom-false-value-to-bool"),
        pytest.param({"col2": "no"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col2": False}, id="cast-no-to-bool"),
        pytest.param({"col2": "10"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col2": "10"}, id="cannot-cast-to-bool"),
        pytest.param({"col3": "1.1"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col3": "1.1"}, id="cannot-cast-to-int"),
        pytest.param({"col4": "asdf"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col4": "asdf"}, id="cannot-cast-to-float"),
        pytest.param({"col6": "{'a': 'b'}"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col6": "{'a': 'b'}"}, id="cannot-cast-to-dict"),
        pytest.param({"col7": "['a', 'b']"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col7": "['a', 'b']"}, id="cannot-cast-to-list-of-ints"),
        pytest.param({"col8": "['a', 'b']"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col8": "['a', 'b']"}, id="cannot-cast-to-list-of-strings"),
        pytest.param({"col9": "['a', 'b']"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col9": "['a', 'b']"}, id="cannot-cast-to-list-of-objects"),
        pytest.param({"col10": "x"}, DEFAULT_TRUE_VALUES, DEFAULT_FALSE_VALUES, {"col10": "x"}, id="item-not-in-props-doesn't-error"),
    ]
)
def test_cast_to_python_type(row, true_values, false_values, expected_output):
    csv_format = CsvFormat(true_values=true_values, false_values=false_values)
    assert _cast_types(row, PROPERTY_TYPES, csv_format, logger) == expected_output


@pytest.mark.parametrize(
    "reader_values, expected_rows", [
        pytest.param([{"col1": "1", "col2": None}], None, id="raise_exception_if_any_value_is_none"),
        pytest.param([{"col1": "1", "col2": "2"}], [{"col1": "1", "col2": "2"}], id="read_no_cast"),
    ]
)
def test_read_and_cast_types(reader_values, expected_rows):
    reader = MagicMock()
    reader.__iter__.return_value = reader_values
    schema = {}
    config_format = CsvFormat()
    logger = Mock()

    parser = CsvParser()

    expected_rows = expected_rows
    if expected_rows is None:
        with pytest.raises(RecordParseError):
            list(parser._read_and_cast_types(reader, schema, config_format, logger))
    else:
        assert expected_rows == list(parser._read_and_cast_types(reader, schema, config_format, logger))
