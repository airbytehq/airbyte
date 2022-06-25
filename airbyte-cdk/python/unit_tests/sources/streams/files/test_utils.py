#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import time
from typing import Any, Mapping, Tuple

import airbyte_cdk.sources.streams.files.utils as utils
import pyarrow as pa
import pytest

logger = logging.getLogger("airbyte")


def external_process_failure():
    try:
        1 / 0
    except Exception as e:
        return (None, e)


def external_process_success(dummy_arg):
    return (dummy_arg, None)


def external_process_timeout():
    time.sleep(6)


class TestFilesUtils:
    def test_run_in_external_process_failure(self):
        with pytest.raises(ZeroDivisionError):
            utils.run_in_external_process(external_process_failure, 2, 4, logger, [])

    def test_run_in_external_process_success(self):
        arg_to_pass = "7b372d17-c3d1-4e44-95ed-b8edb3790160"
        return_val = utils.run_in_external_process(external_process_success, 2, 4, logger, [arg_to_pass])
        assert return_val == arg_to_pass

    def test_run_in_external_process_timeout(self):
        with pytest.raises(TimeoutError):
            utils.run_in_external_process(external_process_timeout, 1, 2, logger, [])

    def test_get_value_or_json_if_empty_string(self):
        assert utils.get_value_or_json_if_empty_string("   abcd efgh   ") == "abcd efgh"
        assert utils.get_value_or_json_if_empty_string("") == "{}"

    @pytest.mark.parametrize(  # testing all datatypes as laid out here: https://json-schema.org/understanding-json-schema/reference/type.html
        "input_json_type, output_pyarrow_type",
        [
            ("string", pa.large_string()),
            ("number", pa.float64()),
            ("integer", pa.int64()),
            ("object", pa.large_string()),
            ("array", pa.large_string()),
            ("boolean", pa.bool_()),
            ("null", pa.large_string()),
        ],
    )
    def test_json_type_to_pyarrow_type(self, input_json_type: str, output_pyarrow_type: Any) -> None:
        # Json -> PyArrow direction
        logger.info(f"asserting that JSON type '{input_json_type}' converts to PyArrow type '{output_pyarrow_type}'...")
        assert utils.json_type_to_pyarrow_type(input_json_type, logger) == output_pyarrow_type

    @pytest.mark.parametrize(  # testing all datatypes as laid out here: https://arrow.apache.org/docs/python/api/datatypes.html
        "input_pyarrow_types, output_json_type",
        [
            ((pa.null(),), "string"),  # null type
            ((pa.bool_(),), "boolean"),  # boolean type
            (
                (pa.int8(), pa.int16(), pa.int32(), pa.int64(), pa.uint8(), pa.uint16(), pa.uint32(), pa.uint64()),
                "integer",
            ),  # integer types
            ((pa.float16(), pa.float32(), pa.float64(), pa.decimal128(5, 10), pa.decimal256(3, 8)), "number"),  # number types
            ((pa.time32("s"), pa.time64("ns"), pa.timestamp("ms"), pa.date32(), pa.date64()), "string"),  # temporal types
            ((pa.binary(), pa.large_binary()), "string"),  # binary types
            ((pa.string(), pa.utf8(), pa.large_string(), pa.large_utf8()), "string"),  # string types
            ((pa.list_(pa.string()), pa.large_list(pa.timestamp("us"))), "string"),  # array types
            ((pa.map_(pa.string(), pa.float32()), pa.dictionary(pa.int16(), pa.list_(pa.string()))), "string"),  # object types
        ],
    )
    def test_json_type_to_pyarrow_type_reverse(self, input_pyarrow_types: Tuple[Any], output_json_type: str) -> None:
        # PyArrow -> Json direction (reverse=True)
        for typ in input_pyarrow_types:
            logger.info(f"asserting that PyArrow type '{typ}' converts to JSON type '{output_json_type}'...")
            assert utils.json_type_to_pyarrow_type(typ, logger, reverse=True) == output_json_type

    @pytest.mark.parametrize(  # if expecting fail, put pyarrow_schema as None
        "json_schema, pyarrow_schema",
        [
            (
                {"a": "string", "b": "number", "c": "integer", "d": "object", "e": "array", "f": "boolean", "g": "null"},
                {
                    "a": pa.large_string(),
                    "b": pa.float64(),
                    "c": pa.int64(),
                    "d": pa.large_string(),
                    "e": pa.large_string(),
                    "f": pa.bool_(),
                    "g": pa.large_string(),
                },
            ),
            ({"single_column": "object"}, {"single_column": pa.large_string()}),
            ({}, {}),
            ({"a": "NOT A REAL TYPE", "b": "another fake type"}, {"a": pa.large_string(), "b": pa.large_string()}),
            (["string", "object"], None),  # bad input type
        ],
    )
    def test_json_schema_to_pyarrow_schema(self, json_schema: Mapping[str, Any], pyarrow_schema: Mapping[str, Any]) -> None:
        # Json -> PyArrow direction
        if pyarrow_schema is not None:
            assert utils.json_schema_to_pyarrow_schema(json_schema, logger) == pyarrow_schema
        else:
            with pytest.raises(Exception) as e_info:
                utils.json_schema_to_pyarrow_schema(json_schema, logger)
                logger.debug(str(e_info))

    @pytest.mark.parametrize(  # if expecting fail, put json_schema as None
        "pyarrow_schema, json_schema",
        [
            (
                {
                    "a": pa.utf8(),
                    "b": pa.float16(),
                    "c": pa.uint32(),
                    "d": pa.map_(pa.string(), pa.float32()),
                    "e": pa.bool_(),
                    "f": pa.date64(),
                },
                {"a": "string", "b": "number", "c": "integer", "d": "string", "e": "boolean", "f": "string"},
            ),
            ({"single_column": pa.int32()}, {"single_column": "integer"}),
            ({}, {}),
            ({"a": "NOT A REAL TYPE", "b": "another fake type"}, {"a": "string", "b": "string"}),
            (["string", "object"], None),  # bad input type
        ],
    )
    def test_json_schema_to_pyarrow_schema_reverse(self, pyarrow_schema: Mapping[str, Any], json_schema: Mapping[str, Any]) -> None:
        # PyArrow -> Json direction (reverse=True)
        if json_schema is not None:
            assert utils.json_schema_to_pyarrow_schema(pyarrow_schema, logger, reverse=True) == json_schema
        else:
            with pytest.raises(Exception) as e_info:
                utils.json_schema_to_pyarrow_schema(pyarrow_schema, logger, reverse=True)
                logger.debug(str(e_info))
