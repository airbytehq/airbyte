#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import csv
import io
import logging
import unittest
from typing import Any, Dict, Generator, List, Set
from unittest.mock import Mock
from unittest import TestCase

import pytest
from airbyte_cdk.sources.file_based.config.csv_format import DEFAULT_FALSE_VALUES, DEFAULT_TRUE_VALUES, CsvFormat
from airbyte_cdk.sources.file_based.exceptions import RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.file_types.csv_parser import _CsvReader, CsvParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile

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
def test_cast_to_python_type(row: Dict[str, str], true_values: Set[str], false_values: Set[str], expected_output: Dict[str, Any]) -> None:
    csv_format = CsvFormat(true_values=true_values, false_values=false_values)
    assert CsvParser._cast_types(row, PROPERTY_TYPES, csv_format, logger) == expected_output


_DEFAULT_TRUE_VALUES = {"yes", "yeah", "right"}
_DEFAULT_FALSE_VALUES = {"no", "nop", "wrong"}


class SchemaInferrenceTestCase(TestCase):
    def setUp(self) -> None:
        self._config_format = CsvFormat()
        self._config_format.true_values = _DEFAULT_TRUE_VALUES
        self._config_format.false_values = _DEFAULT_FALSE_VALUES
        self._config = Mock()
        self._config.format.get.return_value = self._config_format

        self._file = Mock(spec=RemoteFile)
        self._stream_reader = Mock(spec=AbstractFileBasedStreamReader)
        self._logger = Mock(spec=logging.Logger)
        self._csv_reader = Mock(spec=_CsvReader)
        self._parser = CsvParser(self._csv_reader)

    def test_given_booleans_only_when_infer_schema_then_type_is_boolean(self) -> None:
        self._test_infer_schema(list(_DEFAULT_TRUE_VALUES.union(_DEFAULT_FALSE_VALUES)), "boolean")

    def test_given_numbers_only_when_infer_schema_then_type_is_number(self) -> None:
        self._test_infer_schema(["2", "90329", "2.312"], "number")

    def test_given_arrays_only_when_infer_schema_then_type_is_array(self) -> None:
        self._test_infer_schema(['["first_item", "second_item"]', '["first_item_again", "second_item_again"]'], "array")

    def test_given_objects_only_when_infer_schema_then_type_is_object(self) -> None:
        self._test_infer_schema(['{"object1_key": 1}', '{"object2_key": 2}'], "object")

    def test_given_arrays_and_objects_only_when_infer_schema_then_type_is_object(self) -> None:
        self._test_infer_schema(['["first_item", "second_item"]', '{"an_object_key": "an_object_value"}'], "object")

    def test_given_strings_and_objects_only_when_infer_schema_then_type_is_object(self) -> None:
        self._test_infer_schema(['["first_item", "second_item"]', "this is a string"], "object")

    def test_given_strings_only_when_infer_schema_then_type_is_string(self) -> None:
        self._test_infer_schema(["a string", "another string"], "string")

    def _test_infer_schema(self, rows: List[str], expected_type: str) -> None:
        self._csv_reader.read_data.return_value = ({"header": row} for row in rows)
        inferred_schema = self._infer_schema()
        assert inferred_schema == {"header": {"type": expected_type}}

    def test_given_big_file_when_infer_schema_then_stop_early(self) -> None:
        self._csv_reader.read_data.return_value = ({"header": row} for row in ["2" * 1_000_000] + ["this is a string"])
        inferred_schema = self._infer_schema()
        # since the type is number, we know the string at the end was not considered
        assert inferred_schema == {"header": {"type": "number"}}

    def _infer_schema(self):
        loop = asyncio.new_event_loop()
        task = loop.create_task(self._parser.infer_schema(self._config, self._file, self._stream_reader, self._logger))
        loop.run_until_complete(task)
        return task.result()


class CsvFileBuilder:
    def __init__(self) -> None:
        self._prefixed_rows: List[str] = []
        self._data: List[str] = []

    def with_prefixed_rows(self, rows: List[str]) -> 'CsvFileBuilder':
        self._prefixed_rows = rows
        return self

    def with_data(self, data: List[str]) -> 'CsvFileBuilder':
        self._data = data
        return self

    def build(self) -> io.StringIO:
        return io.StringIO("\n".join(self._prefixed_rows + self._data))


class CsvReaderTest(unittest.TestCase):
    _CONFIG_NAME = "config_name"

    def setUp(self) -> None:
        self._config_format = CsvFormat()
        self._config = Mock()
        self._config.name = self._CONFIG_NAME
        self._config.format.get.return_value = self._config_format

        self._file = Mock(spec=RemoteFile)
        self._stream_reader = Mock(spec=AbstractFileBasedStreamReader)
        self._logger = Mock(spec=logging.Logger)
        self._csv_reader = _CsvReader()

    def test_given_skip_rows_when_read_data_then_do_not_considered_prefixed_rows(self) -> None:
        self._config_format.skip_rows_before_header = 2
        self._stream_reader.open_file.return_value = CsvFileBuilder().with_prefixed_rows(["first line", "second line"]).with_data([
            "header",
            "a value",
            "another value",
        ]).build()

        data_generator = self._read_data()

        assert list(data_generator) == [{"header": "a value"}, {"header": "another value"}]

    def test_given_autogenerated_headers_when_read_data_then_generate_headers_with_format_fX(self) -> None:
        self._config_format.autogenerate_column_names = True
        self._stream_reader.open_file.return_value = CsvFileBuilder().with_data([
            '0,1,2,3,4,5,6'
        ]).build()

        data_generator = self._read_data()

        assert list(data_generator) == [{"f0": "0", "f1": "1", "f2": "2", "f3": "3", "f4": "4", "f5": "5", "f6": "6"}]

    def test_given_skip_rows_after_header_when_read_data_then_do_not_parse_skipped_rows(self) -> None:
        self._config_format.skip_rows_after_header = 1
        self._stream_reader.open_file.return_value = CsvFileBuilder().with_data([
            "header1,header2",
            "skipped row: important that the is no comma in this string to test if columns do not match in skipped rows",
            "a value 1,a value 2",
            "another value 1,another value 2"
        ]).build()

        data_generator = self._read_data()

        assert list(data_generator) == [
            {"header1": "a value 1", "header2": "a value 2"},
            {"header1": "another value 1", "header2": "another value 2"}
        ]

    def test_given_quote_delimiter_when_read_data_then_parse_properly(self) -> None:
        self._config_format.delimiter = "|"
        self._stream_reader.open_file.return_value = CsvFileBuilder().with_data([
            "header1|header2",
            "a value 1|a value 2",
        ]).build()

        data_generator = self._read_data()

        assert list(data_generator) == [{"header1": "a value 1", "header2": "a value 2"}]

    def test_given_quote_char_when_read_data_then_parse_properly(self) -> None:
        self._config_format.quote_char = "|"
        self._stream_reader.open_file.return_value = CsvFileBuilder().with_data([
            "header1,header2",
            "|a,value,1|,|a,value,2|",
        ]).build()

        data_generator = self._read_data()

        assert list(data_generator) == [{"header1": "a,value,1", "header2": "a,value,2"}]

    def test_given_escape_char_when_read_data_then_parse_properly(self) -> None:
        self._config_format.escape_char = "|"
        self._stream_reader.open_file.return_value = CsvFileBuilder().with_data([
            "header1,header2",
            '"a |"value|", 1",a value 2',
        ]).build()

        data_generator = self._read_data()

        assert list(data_generator) == [{"header1": 'a "value", 1', "header2": "a value 2"}]

    def test_given_double_quote_on_when_read_data_then_parse_properly(self) -> None:
        self._config_format.double_quote = True
        self._stream_reader.open_file.return_value = CsvFileBuilder().with_data([
            "header1,header2",
            '1,"Text with doublequote: ""This is a text."""',
        ]).build()

        data_generator = self._read_data()

        assert list(data_generator) == [{"header1": "1", "header2": 'Text with doublequote: "This is a text."'}]

    def test_given_double_quote_off_when_read_data_then_parse_properly(self) -> None:
        self._config_format.double_quote = False
        self._stream_reader.open_file.return_value = CsvFileBuilder().with_data([
            "header1,header2",
            '1,"Text with doublequote: ""This is a text."""',
        ]).build()

        data_generator = self._read_data()

        assert list(data_generator) == [{"header1": "1", "header2": 'Text with doublequote: "This is a text."""'}]

    def test_given_generator_closed_when_read_data_then_unregister_dialect(self) -> None:
        self._stream_reader.open_file.return_value = CsvFileBuilder().with_data([
            "header",
            "a value",
            "another value",
        ]).build()

        data_generator = self._read_data()
        next(data_generator)
        assert f"{self._CONFIG_NAME}_config_dialect" in csv.list_dialects()
        data_generator.close()
        assert f"{self._CONFIG_NAME}_config_dialect" not in csv.list_dialects()

    def test_given_exception_when_read_data_then_unregister_dialect(self) -> None:
        self._stream_reader.open_file.return_value = CsvFileBuilder().with_data([
            "header",
            "a value",
            "too many values,value,value,value",
        ]).build()

        data_generator = self._read_data()
        next(data_generator)
        assert f"{self._CONFIG_NAME}_config_dialect" in csv.list_dialects()

        with pytest.raises(RecordParseError):
            next(data_generator)
        assert f"{self._CONFIG_NAME}_config_dialect" not in csv.list_dialects()

    def _read_data(self) -> Generator[Dict[str, str], None, None]:
        data_generator = self._csv_reader.read_data(
            self._config,
            self._file,
            self._stream_reader,
            self._logger,
            FileReadMode.READ,
        )
        return data_generator
