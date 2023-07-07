#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Mapping

import pyarrow as pa
import pytest
from airbyte_cdk.sources.file_based.file_types import ParquetParser


@pytest.mark.parametrize(
    "parquet_type, expected_type",
    [
        pytest.param(pa.bool_(), {"type": "boolean"}, id="test_parquet_bool"),
        pytest.param(pa.int8(), {"type": "integer"}, id="test_parquet_int8"),
        pytest.param(pa.int16(), {"type": "integer"}, id="test_parquet_int16"),
        pytest.param(pa.int32(), {"type": "integer"}, id="test_parquet_int32"),
        pytest.param(pa.uint8(), {"type": "integer"}, id="test_parquet_uint8"),
        pytest.param(pa.uint16(), {"type": "integer"}, id="test_parquet_uint16"),
        pytest.param(pa.uint32(), {"type": "integer"}, id="test_parquet_uint32"),
        pytest.param(pa.float16(), {"type": "number"}, id="test_parquet_float16"),
        pytest.param(pa.float32(), {"type": "number"}, id="test_parquet_float32"),
        pytest.param(pa.float64(), {"type": "number"}, id="test_parquet_float64"),
        pytest.param(pa.time32("s"), {"type": "string"}, id="test_parquet_time32s"),
        pytest.param(pa.time32("ms"), {"type": "string"}, id="test_parquet_time32ms"),
        pytest.param(pa.time64("us"), {"type": "string"}, id="test_parquet_time64us"),
        pytest.param(pa.time64("ns"), {"type": "string"}, id="test_parquet_time64us"),
        pytest.param(pa.timestamp("s"), {"type": "string", "format": "date-time"}, id="test_parquet_timestamps_s"),
        pytest.param(pa.timestamp("ms"), {"type": "string", "format": "date-time"}, id="test_parquet_timestamp_ms"),
        pytest.param(pa.timestamp("s", "utc"), {"type": "string", "format": "date-time"}, id="test_parquet_timestamps_s_with_tz"),
        pytest.param(pa.timestamp("ms", "est"), {"type": "string", "format": "date-time"}, id="test_parquet_timestamps_ms_with_tz"),
        pytest.param(pa.date32(), {"type": "string", "format": "date"}, id="test_parquet_date32"),
        pytest.param(pa.date64(), {"type": "string", "format": "date"}, id="test_parquet_date64"),
        pytest.param(pa.duration("s"), {"type": "integer"}, id="test_duration_s"),
        pytest.param(pa.duration("ms"), {"type": "integer"}, id="test_duration_ms"),
        pytest.param(pa.duration("us"), {"type": "integer"}, id="test_duration_us"),
        pytest.param(pa.duration("ns"), {"type": "integer"}, id="test_duration_ns"),
        pytest.param(pa.month_day_nano_interval(), None, id="test_parquet_month_day_nano_interval"),
        pytest.param(pa.binary(), {"type": "string"}, id="test_binary"),
        pytest.param(pa.string(), {"type": "string"}, id="test_parquet_string"),
        pytest.param(pa.utf8(), {"type": "string"}, id="test_utf8"),
        pytest.param(pa.large_binary(), {"type": "string"}, id="test_large_binary"),
        pytest.param(pa.large_string(), {"type": "string"}, id="test_large_string"),
        pytest.param(pa.large_utf8(), {"type": "string"}, id="test_large_utf8"),
        pytest.param(pa.dictionary(pa.int32(), pa.string()), {"type": "object"}, id="test_dictionary"),
        pytest.param(pa.struct([pa.field("field", pa.int32())]), {"type": "object"}, id="test_dictionary"),
        pytest.param(pa.list_(pa.int32()), {"type": "array"}, id="test_list"),
        pytest.param(pa.large_list(pa.int32()), {"type": "array"}, id="test_large_list"),
        pytest.param(pa.decimal128(2), {"type": "string"}, id="test_decimal128"),
        pytest.param(pa.decimal256(2), {"type": "string"}, id="test_decimal256"),
    ]
)
def test_parquet_parser(parquet_type: pa.DataType, expected_type: Mapping[str, str]) -> None:
    if expected_type is None:
        with pytest.raises(ValueError):
            ParquetParser.parquet_type_to_schema_type(parquet_type)
    else:
        assert ParquetParser.parquet_type_to_schema_type(parquet_type) == expected_type
