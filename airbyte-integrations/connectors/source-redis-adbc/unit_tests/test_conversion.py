# Copyright (c) 2026 Albert Wong
# SPDX-License-Identifier: MIT
import base64
from decimal import Decimal

import jsonschema
import pyarrow as pa
import pytest
from source_redis_adbc.conversion import ConversionError, batch_records, field_schema, scalar_to_json, schema_to_json


@pytest.mark.parametrize(
    "dtype,value,expected",
    [
        (pa.int64(), 9223372036854775807, "9223372036854775807"),
        (pa.uint64(), 18446744073709551615, "18446744073709551615"),
        (pa.int32(), 2147483647, 2147483647),
        (pa.bool_(), True, True),
        (pa.decimal128(38, 9), Decimal("12345678901234567890.123456789"), "12345678901234567890.123456789"),
        (pa.binary(), b"\x00\xff", "AP8="),
        (pa.string(), "hello", "hello"),
        (pa.string(), None, None),
        (pa.date32(), 0, "1970-01-01"),
        (pa.timestamp("ns"), 123456789, "1970-01-01T00:00:00.123456789"),
        (pa.time64("ns"), 1, "00:00:00.000000001"),
        (pa.list_(pa.int64()), [1, None, 2**60], ["1", None, str(2**60)]),
        (pa.struct([pa.field("x", pa.int64())]), {"x": 2**60}, {"x": str(2**60)}),
    ],
)
def test_explicit_conversion_matches_schema(dtype, value, expected):
    scalar = pa.scalar(value, type=dtype)
    actual = scalar_to_json(scalar, dtype)
    assert actual == expected
    jsonschema.validate(actual, field_schema(pa.field("value", dtype)))


def test_dictionary_and_null():
    arr = pa.array(["red", None, "blue"]).dictionary_encode()
    batch = pa.record_batch([arr], names=["color"])
    assert list(batch_records(batch)) == [{"color": "red"}, {"color": None}, {"color": "blue"}]
    assert field_schema(pa.field("nothing", pa.null())) == {"type": "null"}


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_floats_fail(value):
    with pytest.raises(ConversionError, match="Non-finite"):
        scalar_to_json(pa.scalar(value), pa.float64())


@pytest.mark.parametrize("dtype", [pa.duration("us"), pa.map_(pa.string(), pa.int64()), pa.month_day_nano_interval()])
def test_unsupported_types_fail_discovery(dtype):
    with pytest.raises(ConversionError, match="Unsupported Arrow type"):
        schema_to_json(pa.schema([pa.field("x", dtype)]))


def test_duplicate_field_names_fail():
    with pytest.raises(ConversionError, match="Duplicate"):
        schema_to_json(pa.schema([("x", pa.int64()), ("x", pa.string())]))


def test_binary_and_timezone():
    for dtype in [pa.binary(3), pa.large_binary(), pa.binary_view()]:
        assert scalar_to_json(pa.scalar(b"abc", dtype), dtype) == base64.b64encode(b"abc").decode()
    value = scalar_to_json(pa.scalar(123456789, pa.timestamp("ns", "UTC")), pa.timestamp("ns", "UTC"))
    assert value in ("1970-01-01T00:00:00.123456789Z", "1970-01-01T00:00:00.123456789+00:00")
