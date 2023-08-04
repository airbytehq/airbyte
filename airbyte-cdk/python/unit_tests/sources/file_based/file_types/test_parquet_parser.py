#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import datetime
import math
from typing import Any, Mapping, Union
from unittest.mock import Mock

import pyarrow as pa
import pytest
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from airbyte_cdk.sources.file_based.config.parquet_format import ParquetFormat
from airbyte_cdk.sources.file_based.file_types import ParquetParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from pyarrow import Scalar

_default_parquet_format = ParquetFormat()
_decimal_as_float_parquet_format = ParquetFormat(decimal_as_float=True)


@pytest.mark.parametrize(
    "parquet_type, expected_type, parquet_format",
    [
        pytest.param(pa.bool_(), {"type": "boolean"}, _default_parquet_format, id="test_parquet_bool"),
        pytest.param(pa.int8(), {"type": "integer"}, _default_parquet_format, id="test_parquet_int8"),
        pytest.param(pa.int16(), {"type": "integer"}, _default_parquet_format, id="test_parquet_int16"),
        pytest.param(pa.int32(), {"type": "integer"}, _default_parquet_format, id="test_parquet_int32"),
        pytest.param(pa.int64(), {"type": "integer"}, _default_parquet_format, id="test_parquet_int64"),
        pytest.param(pa.uint8(), {"type": "integer"}, _default_parquet_format, id="test_parquet_uint8"),
        pytest.param(pa.uint16(), {"type": "integer"}, _default_parquet_format, id="test_parquet_uint16"),
        pytest.param(pa.uint32(), {"type": "integer"}, _default_parquet_format, id="test_parquet_uint32"),
        pytest.param(pa.uint64(), {"type": "integer"}, _default_parquet_format, id="test_parquet_uint64"),
        pytest.param(pa.float16(), {"type": "number"}, _default_parquet_format, id="test_parquet_float16"),
        pytest.param(pa.float32(), {"type": "number"}, _default_parquet_format, id="test_parquet_float32"),
        pytest.param(pa.float64(), {"type": "number"}, _default_parquet_format, id="test_parquet_float64"),
        pytest.param(pa.time32("s"), {"type": "string"}, _default_parquet_format, id="test_parquet_time32s"),
        pytest.param(pa.time32("ms"), {"type": "string"}, _default_parquet_format, id="test_parquet_time32ms"),
        pytest.param(pa.time64("us"), {"type": "string"}, _default_parquet_format, id="test_parquet_time64us"),
        pytest.param(pa.time64("ns"), {"type": "string"}, _default_parquet_format, id="test_parquet_time64us"),
        pytest.param(pa.timestamp("s"), {"type": "string", "format": "date-time"}, _default_parquet_format, id="test_parquet_timestamps_s"),
        pytest.param(pa.timestamp("ms"), {"type": "string", "format": "date-time"}, _default_parquet_format,
                     id="test_parquet_timestamp_ms"),
        pytest.param(pa.timestamp("s", "utc"), {"type": "string", "format": "date-time"}, _default_parquet_format,
                     id="test_parquet_timestamps_s_with_tz"),
        pytest.param(pa.timestamp("ms", "est"), {"type": "string", "format": "date-time"}, _default_parquet_format,
                     id="test_parquet_timestamps_ms_with_tz"),
        pytest.param(pa.date32(), {"type": "string", "format": "date"}, _default_parquet_format, id="test_parquet_date32"),
        pytest.param(pa.date64(), {"type": "string", "format": "date"}, _default_parquet_format, id="test_parquet_date64"),
        pytest.param(pa.duration("s"), {"type": "integer"}, _default_parquet_format, id="test_duration_s"),
        pytest.param(pa.duration("ms"), {"type": "integer"}, _default_parquet_format, id="test_duration_ms"),
        pytest.param(pa.duration("us"), {"type": "integer"}, _default_parquet_format, id="test_duration_us"),
        pytest.param(pa.duration("ns"), {"type": "integer"}, _default_parquet_format, id="test_duration_ns"),
        pytest.param(pa.month_day_nano_interval(), {"type": "array"}, _default_parquet_format, id="test_parquet_month_day_nano_interval"),
        pytest.param(pa.binary(), {"type": "string"}, _default_parquet_format, id="test_binary"),
        pytest.param(pa.binary(2), {"type": "string"}, _default_parquet_format, id="test_fixed_size_binary"),
        pytest.param(pa.string(), {"type": "string"}, _default_parquet_format, id="test_parquet_string"),
        pytest.param(pa.utf8(), {"type": "string"}, _default_parquet_format, id="test_utf8"),
        pytest.param(pa.large_binary(), {"type": "string"}, _default_parquet_format, id="test_large_binary"),
        pytest.param(pa.large_string(), {"type": "string"}, _default_parquet_format, id="test_large_string"),
        pytest.param(pa.large_utf8(), {"type": "string"}, _default_parquet_format, id="test_large_utf8"),
        pytest.param(pa.dictionary(pa.int32(), pa.string()), {"type": "object"}, _default_parquet_format, id="test_dictionary"),
        pytest.param(pa.struct([pa.field("field", pa.int32())]), {"type": "object"}, _default_parquet_format, id="test_struct"),
        pytest.param(pa.list_(pa.int32()), {"type": "array"}, _default_parquet_format, id="test_list"),
        pytest.param(pa.large_list(pa.int32()), {"type": "array"}, _default_parquet_format, id="test_large_list"),
        pytest.param(pa.decimal128(2), {"type": "string"}, _default_parquet_format, id="test_decimal128"),
        pytest.param(pa.decimal256(2), {"type": "string"}, _default_parquet_format, id="test_decimal256"),
        pytest.param(pa.decimal128(2), {"type": "number"}, _decimal_as_float_parquet_format, id="test_decimal128_as_float"),
        pytest.param(pa.decimal256(2), {"type": "number"}, _decimal_as_float_parquet_format, id="test_decimal256_as_float"),
        pytest.param(pa.map_(pa.int32(), pa.int32()), {"type": "object"}, _default_parquet_format, id="test_map"),
        pytest.param(pa.null(), {"type": "null"}, _default_parquet_format, id="test_null"),
    ]
)
def test_type_mapping(parquet_type: pa.DataType, expected_type: Mapping[str, str], parquet_format: ParquetFormat) -> None:
    if expected_type is None:
        with pytest.raises(ValueError):
            ParquetParser.parquet_type_to_schema_type(parquet_type, parquet_format)
    else:
        assert ParquetParser.parquet_type_to_schema_type(parquet_type, parquet_format) == expected_type


@pytest.mark.parametrize(
    "pyarrow_type, parquet_format, parquet_object, expected_value",
    [
        pytest.param(pa.bool_(), _default_parquet_format, True, True, id="test_bool"),
        pytest.param(pa.int8(), _default_parquet_format, -1, -1, id="test_int8"),
        pytest.param(pa.int16(), _default_parquet_format, 2, 2, id="test_int16"),
        pytest.param(pa.int32(), _default_parquet_format, 3, 3, id="test_int32"),
        pytest.param(pa.int64(), _default_parquet_format, 4, 4, id="test_int64"),
        pytest.param(pa.uint8(), _default_parquet_format, 4, 4, id="test_parquet_uint8"),
        pytest.param(pa.uint16(), _default_parquet_format, 5, 5, id="test_parquet_uint16"),
        pytest.param(pa.uint32(), _default_parquet_format, 6, 6, id="test_parquet_uint32"),
        pytest.param(pa.uint64(), _default_parquet_format, 6, 6, id="test_parquet_uint64"),
        pytest.param(pa.float32(), _default_parquet_format, 2.7, 2.7, id="test_parquet_float32"),
        pytest.param(pa.float64(), _default_parquet_format, 3.14, 3.14, id="test_parquet_float64"),
        pytest.param(pa.time32("s"), _default_parquet_format, datetime.time(1, 2, 3), "01:02:03", id="test_parquet_time32s"),
        pytest.param(pa.time32("ms"), _default_parquet_format, datetime.time(3, 4, 5), "03:04:05", id="test_parquet_time32ms"),
        pytest.param(pa.time64("us"), _default_parquet_format, datetime.time(6, 7, 8), "06:07:08", id="test_parquet_time64us"),
        pytest.param(pa.time64("ns"), _default_parquet_format, datetime.time(9, 10, 11), "09:10:11", id="test_parquet_time64us"),
        pytest.param(pa.timestamp("s"), _default_parquet_format, datetime.datetime(2023, 7, 7, 10, 11, 12), "2023-07-07T10:11:12",
                     id="test_parquet_timestamps_s"),
        pytest.param(pa.timestamp("ms"), _default_parquet_format, datetime.datetime(2024, 8, 8, 11, 12, 13), "2024-08-08T11:12:13",
                     id="test_parquet_timestamp_ms"),
        pytest.param(pa.timestamp("s", "utc"), _default_parquet_format,
                     datetime.datetime(2020, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc),
                     "2020-01-01T01:01:01+00:00", id="test_parquet_timestamps_s_with_tz"),
        pytest.param(pa.timestamp("ms", "utc"), _default_parquet_format, datetime.datetime(2021, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                     "2021-02-03T04:05:00+00:00", id="test_parquet_timestamps_ms_with_tz"),
        pytest.param(pa.date32(), _default_parquet_format, datetime.date(2023, 7, 7), "2023-07-07", id="test_parquet_date32"),
        pytest.param(pa.date64(), _default_parquet_format, datetime.date(2023, 7, 8), "2023-07-08", id="test_parquet_date64"),
        pytest.param(pa.duration("s"), _default_parquet_format, 12345, 12345, id="test_duration_s"),
        pytest.param(pa.duration("ms"), _default_parquet_format, 12345, 12345, id="test_duration_ms"),
        pytest.param(pa.duration("us"), _default_parquet_format, 12345, 12345, id="test_duration_us"),
        pytest.param(pa.duration("ns"), _default_parquet_format, 12345, 12345, id="test_duration_ns"),
        pytest.param(pa.month_day_nano_interval(), _default_parquet_format, datetime.timedelta(days=3, microseconds=4), [0, 3, 4000],
                     id="test_parquet_month_day_nano_interval"),
        pytest.param(pa.binary(), _default_parquet_format, b"this is a binary string", "this is a binary string", id="test_binary"),
        pytest.param(pa.binary(2), _default_parquet_format, b"t1", "t1", id="test_fixed_size_binary"),
        pytest.param(pa.string(), _default_parquet_format, "this is a string", "this is a string", id="test_parquet_string"),
        pytest.param(pa.utf8(), _default_parquet_format, "utf8".encode("utf8"), "utf8", id="test_utf8"),
        pytest.param(pa.large_binary(), _default_parquet_format, b"large binary string", "large binary string", id="test_large_binary"),
        pytest.param(pa.large_string(), _default_parquet_format, "large string", "large string", id="test_large_string"),
        pytest.param(pa.large_utf8(), _default_parquet_format, "large utf8", "large utf8", id="test_large_utf8"),
        pytest.param(pa.struct([pa.field("field", pa.int32())]), _default_parquet_format, {"field": 1}, {"field": 1}, id="test_struct"),
        pytest.param(pa.list_(pa.int32()), _default_parquet_format, [1, 2, 3], [1, 2, 3], id="test_list"),
        pytest.param(pa.large_list(pa.int32()), _default_parquet_format, [4, 5, 6], [4, 5, 6], id="test_large_list"),
        pytest.param(pa.decimal128(5, 3), _default_parquet_format, 12, "12.000", id="test_decimal128"),
        pytest.param(pa.decimal256(8, 2), _default_parquet_format, 13, "13.00", id="test_decimal256"),
        pytest.param(pa.decimal128(5, 3), _decimal_as_float_parquet_format, 12, 12.000, id="test_decimal128"),
        pytest.param(pa.decimal256(8, 2), _decimal_as_float_parquet_format, 13, 13.00, id="test_decimal256"),
        pytest.param(pa.map_(pa.string(), pa.int32()), _default_parquet_format, {"hello": 1, "world": 2}, {"hello": 1, "world": 2},
                     id="test_map"),
        pytest.param(pa.null(), _default_parquet_format, None, None, id="test_null"),
    ]
)
def test_value_transformation(pyarrow_type: pa.DataType, parquet_format: ParquetFormat, parquet_object: Scalar,
                              expected_value: Any) -> None:
    pyarrow_value = pa.array([parquet_object], type=pyarrow_type)[0]
    py_value = ParquetParser._to_output_value(pyarrow_value, parquet_format)
    if isinstance(py_value, float):
        assert math.isclose(py_value, expected_value, abs_tol=0.01)
    else:
        assert py_value == expected_value


def test_value_dictionary() -> None:
    # Setting the dictionary is more involved than other data types so we test it in a separate test
    dictionary_values = ["apple", "banana", "cherry"]
    indices = [0, 1, 2, 0, 1]
    indices_array = pa.array(indices, type=pa.int8())
    dictionary = pa.DictionaryArray.from_arrays(indices_array, dictionary_values)
    py_value = ParquetParser._to_output_value(dictionary, _default_parquet_format)
    assert py_value == {"indices": [0, 1, 2, 0, 1], "values": ["apple", "banana", "cherry"]}


@pytest.mark.parametrize(
    "file_format", [
        pytest.param(CsvFormat(
            filetype="csv",
            delimiter=",",
            escape_char="\\",
            quote_char='"',
        ), id="test_csv_format"),
        pytest.param(JsonlFormat(), id="test_jsonl_format"),
    ]
)
def test_wrong_file_format(file_format: Union[CsvFormat, JsonlFormat]) -> None:
    parser = ParquetParser()
    config = FileBasedStreamConfig(name="test.parquet", file_type=file_format.filetype, format={file_format.filetype: file_format},
                                   validation_policy="a_validtion_policy")
    file = RemoteFile(uri="s3://mybucket/test.parquet", last_modified=datetime.datetime.now())
    stream_reader = Mock()
    logger = Mock()
    with pytest.raises(ValueError):
        asyncio.get_event_loop().run_until_complete(
            parser.infer_schema(config, file, stream_reader, logger)
        )
