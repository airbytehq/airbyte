# Copyright (c) 2026 Albert Wong
# SPDX-License-Identifier: MIT
"""Explicit, loss-aware Arrow to Airbyte JSON conversion.

Decimal and 64-bit integers use strings to survive JSON consumers which use
IEEE 754 doubles. Unsupported Arrow types fail discovery instead of guessing.
"""

import base64
import math

import pyarrow as pa
import pyarrow.types as pt


class ConversionError(ValueError):
    pass


def _unwrapped(dtype):
    return _unwrapped(dtype.value_type) if pt.is_dictionary(dtype) else dtype


def field_schema(field):
    result = type_schema(field.type)
    if field.nullable and "null" not in result["type"]:
        result["type"] = ["null", result["type"]]
    return result


def type_schema(dtype):
    dtype = _unwrapped(dtype)
    if pt.is_null(dtype):
        return {"type": "null"}
    if pt.is_boolean(dtype):
        return {"type": "boolean"}
    if pt.is_integer(dtype):
        return {"type": "string"} if dtype.bit_width == 64 else {"type": "integer"}
    if pt.is_decimal(dtype):
        return {"type": "string"}
    if pt.is_floating(dtype):
        return {"type": "number"}
    if pt.is_string(dtype) or pt.is_large_string(dtype) or pt.is_string_view(dtype):
        return {"type": "string"}
    if pt.is_binary(dtype) or pt.is_large_binary(dtype) or pt.is_fixed_size_binary(dtype) or pt.is_binary_view(dtype):
        return {"type": "string", "contentEncoding": "base64"}
    if pt.is_timestamp(dtype):
        return {
            "type": "string",
            "format": "date-time",
            "airbyte_type": "timestamp_with_timezone" if dtype.tz else "timestamp_without_timezone",
        }
    if pt.is_date(dtype):
        return {"type": "string", "format": "date"}
    if pt.is_time(dtype):
        return {"type": "string", "format": "time", "airbyte_type": "time_without_timezone"}
    if pt.is_list(dtype) or pt.is_large_list(dtype) or pt.is_fixed_size_list(dtype):
        return {"type": "array", "items": field_schema(dtype.value_field)}
    if pt.is_struct(dtype):
        return schema_to_json(pa.schema(list(dtype)))
    raise ConversionError(f"Unsupported Arrow type: {dtype}")


def schema_to_json(schema):
    if len(set(schema.names)) != len(schema.names):
        raise ConversionError("Duplicate Arrow field names cannot be represented as JSON")
    return {"type": "object", "properties": {f.name: field_schema(f) for f in schema}, "additionalProperties": False}


def scalar_to_json(scalar, dtype):
    if not scalar.is_valid:
        return None
    dtype = _unwrapped(dtype)
    value = scalar.as_py()
    if pt.is_dictionary(scalar.type):
        return scalar_to_json(scalar.value, dtype)
    if pt.is_integer(dtype) and dtype.bit_width == 64:
        return str(value)
    if pt.is_decimal(dtype):
        return format(value, "f")
    if pt.is_floating(dtype) and not math.isfinite(value):
        raise ConversionError("Non-finite floating point values cannot be represented as JSON")
    if pt.is_binary(dtype) or pt.is_large_binary(dtype) or pt.is_fixed_size_binary(dtype) or pt.is_binary_view(dtype):
        return base64.b64encode(value).decode("ascii")
    if pt.is_temporal(dtype) and not pt.is_duration(dtype) and not pt.is_interval(dtype):
        # TimestampScalar.as_py() can truncate nanoseconds without pandas.
        # Arrow's string cast preserves the full stored timestamp precision.
        if pt.is_timestamp(dtype) or pt.is_time(dtype):
            return str(scalar.cast(pa.string()).as_py()).replace(" ", "T", 1)
        return value.isoformat()
    if pt.is_list(dtype) or pt.is_large_list(dtype) or pt.is_fixed_size_list(dtype):
        return [scalar_to_json(v, dtype.value_type) for v in scalar.values]
    if pt.is_struct(dtype):
        return {f.name: scalar_to_json(scalar[f.name], f.type) for f in dtype}
    # Validate the type here too; never pass an unknown Python object to JSON.
    type_schema(dtype)
    return value


def batch_records(batch):
    """Convert row by row; no table or all-batches materialization."""
    for row in range(batch.num_rows):
        yield {field.name: scalar_to_json(batch.column(col)[row], field.type) for col, field in enumerate(batch.schema)}
