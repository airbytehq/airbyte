"""Unit tests for type conversion utilities."""

from datetime import date, datetime, time

import pyarrow as pa

from destination_altertable.type_conversion import (
    convert_to_arrow,
    parse_date,
    parse_time,
    parse_timestamp,
)


class TestParseDate:
    """Tests for parse_date function."""

    def test_none(self):
        assert parse_date(None) is None

    def test_date_object(self):
        d = date(2021, 1, 23)
        assert parse_date(d) == d

    def test_datetime_object(self):
        dt = datetime(2021, 1, 23, 12, 30, 45)
        assert parse_date(dt) == date(2021, 1, 23)

    def test_string_iso_format(self):
        assert parse_date("2021-01-23") == date(2021, 1, 23)

    def test_string_with_bc_suffix(self):
        # BC suffix is stripped (not fully supported but shouldn't crash)
        assert parse_date("2021-01-23 BC") == date(2021, 1, 23)


class TestParseTimestamp:
    """Tests for parse_timestamp function."""

    def test_none(self):
        assert parse_timestamp(None) is None

    def test_datetime_object(self):
        dt = datetime(2022, 11, 22, 1, 23, 45)
        assert parse_timestamp(dt) == dt

    def test_string_with_timezone_offset(self):
        result = parse_timestamp("2022-11-22T01:23:45+05:00")
        assert result.year == 2022
        assert result.month == 11
        assert result.day == 22
        assert result.hour == 1
        assert result.minute == 23
        assert result.second == 45

    def test_string_with_z_suffix(self):
        result = parse_timestamp("2022-11-22T01:23:45Z")
        assert result.year == 2022
        assert result.month == 11
        assert result.day == 22
        assert result.hour == 1
        assert result.minute == 23
        assert result.second == 45
        assert result.tzinfo is not None

    def test_string_with_microseconds(self):
        result = parse_timestamp("2022-11-22T01:23:45.123456+00:00")
        assert result.microsecond == 123456

    def test_string_without_timezone(self):
        result = parse_timestamp("2022-11-22T01:23:45")
        assert result == datetime(2022, 11, 22, 1, 23, 45)

    def test_string_with_bc_suffix(self):
        result = parse_timestamp("2022-11-22T01:23:45Z BC")
        assert result.year == 2022


class TestParseTime:
    """Tests for parse_time function."""

    def test_none(self):
        assert parse_time(None) is None

    def test_time_object(self):
        t = time(1, 23, 45)
        assert parse_time(t) == t

    def test_string_simple(self):
        result = parse_time("01:23:45")
        assert result == time(1, 23, 45)

    def test_string_with_microseconds(self):
        result = parse_time("01:23:45.123456")
        assert result == time(1, 23, 45, 123456)

    def test_string_with_timezone_offset(self):
        # Timezone is stripped for time values
        result = parse_time("01:23:45.123456+05:00")
        assert result == time(1, 23, 45, 123456)

    def test_string_with_z_suffix(self):
        result = parse_time("01:23:45Z")
        assert result == time(1, 23, 45)

    def test_string_with_negative_timezone(self):
        result = parse_time("01:23:45.123456-05:00")
        assert result == time(1, 23, 45, 123456)


class TestConvertToArrowString:
    """Tests for convert_to_arrow with string types."""

    def test_simple_string(self):
        schema = {"type": "string"}
        pa_type, value = convert_to_arrow("hello", schema)
        assert pa_type == pa.string()
        assert value == "hello"

    def test_nullable_string(self):
        schema = {"type": ["null", "string"]}
        pa_type, value = convert_to_arrow("hello", schema)
        assert pa_type == pa.string()
        assert value == "hello"

    def test_null_value(self):
        schema = {"type": "string"}
        pa_type, value = convert_to_arrow(None, schema)
        assert pa_type == pa.string()
        assert value is None


class TestConvertToArrowDate:
    """Tests for convert_to_arrow with date types."""

    def test_date_string(self):
        schema = {"type": "string", "format": "date"}
        pa_type, value = convert_to_arrow("2021-01-23", schema)
        assert pa_type == pa.date32()
        assert value == date(2021, 1, 23)

    def test_date_object(self):
        schema = {"type": "string", "format": "date"}
        pa_type, value = convert_to_arrow(date(2021, 1, 23), schema)
        assert pa_type == pa.date32()
        assert value == date(2021, 1, 23)

    def test_date_null(self):
        schema = {"type": "string", "format": "date"}
        pa_type, value = convert_to_arrow(None, schema)
        assert pa_type == pa.date32()
        assert value is None


class TestConvertToArrowTimestamp:
    """Tests for convert_to_arrow with timestamp types."""

    def test_timestamp_with_timezone(self):
        schema = {"type": "string", "format": "date-time"}
        pa_type, value = convert_to_arrow("2022-11-22T01:23:45Z", schema)
        assert pa_type == pa.timestamp("us", tz="UTC")
        assert isinstance(value, datetime)

    def test_timestamp_with_timezone_explicit(self):
        schema = {
            "type": "string",
            "format": "date-time",
            "airbyte_type": "timestamp_with_timezone",
        }
        pa_type, value = convert_to_arrow("2022-11-22T01:23:45Z", schema)
        assert pa_type == pa.timestamp("us", tz="UTC")

    def test_timestamp_without_timezone(self):
        schema = {
            "type": "string",
            "format": "date-time",
            "airbyte_type": "timestamp_without_timezone",
        }
        pa_type, value = convert_to_arrow("2022-11-22T01:23:45", schema)
        assert pa_type == pa.timestamp("us")
        assert isinstance(value, datetime)

    def test_timestamp_datetime_object(self):
        schema = {"type": "string", "format": "date-time"}
        dt = datetime(2022, 11, 22, 1, 23, 45)
        pa_type, value = convert_to_arrow(dt, schema)
        assert pa_type == pa.timestamp("us", tz="UTC")
        assert value == dt


class TestConvertToArrowTime:
    """Tests for convert_to_arrow with time types."""

    def test_time_without_timezone(self):
        schema = {
            "type": "string",
            "format": "time",
            "airbyte_type": "time_without_timezone",
        }
        pa_type, value = convert_to_arrow("01:23:45", schema)
        assert pa_type == pa.time64("us")
        assert value == time(1, 23, 45)

    def test_time_with_timezone(self):
        schema = {
            "type": "string",
            "format": "time",
            "airbyte_type": "time_with_timezone",
        }
        pa_type, value = convert_to_arrow("01:23:45+05:00", schema)
        assert pa_type == pa.time64("us")
        assert value == time(1, 23, 45)


class TestConvertToArrowNumeric:
    """Tests for convert_to_arrow with numeric types."""

    def test_integer(self):
        schema = {"type": "integer"}
        pa_type, value = convert_to_arrow(42, schema)
        assert pa_type == pa.int64()
        assert value == 42

    def test_number_float(self):
        schema = {"type": "number"}
        pa_type, value = convert_to_arrow(3.14, schema)
        assert pa_type == pa.float64()
        assert value == 3.14

    def test_number_as_integer(self):
        schema = {"type": "number", "airbyte_type": "integer"}
        pa_type, value = convert_to_arrow(42, schema)
        assert pa_type == pa.int64()
        assert value == 42


class TestConvertToArrowBoolean:
    """Tests for convert_to_arrow with boolean types."""

    def test_boolean_true(self):
        schema = {"type": "boolean"}
        pa_type, value = convert_to_arrow(True, schema)
        assert pa_type == pa.bool_()
        assert value is True

    def test_boolean_false(self):
        schema = {"type": "boolean"}
        pa_type, value = convert_to_arrow(False, schema)
        assert pa_type == pa.bool_()
        assert value is False


class TestConvertToArrowFallback:
    """Tests for convert_to_arrow fallback behavior."""

    def test_dict_serialized_to_json(self):
        schema = {}
        pa_type, value = convert_to_arrow({"key": "value"}, schema)
        assert pa_type == pa.string()
        assert value == '{"key": "value"}'

    def test_list_serialized_to_json(self):
        schema = {}
        pa_type, value = convert_to_arrow([1, 2, 3], schema)
        assert pa_type == pa.string()
        assert value == "[1, 2, 3]"

    def test_unknown_type_defaults_to_string(self):
        schema = {"type": "unknown"}
        pa_type, value = convert_to_arrow("test", schema)
        assert pa_type == pa.string()
        assert value == "test"


class TestConvertRecordsToPyArrowTable:
    """Tests for converting a list of records to a PyArrow table."""

    def test_mixed_types_to_pyarrow_table(self):
        """Test converting records with timestamps, structs, and integers to a PyArrow table."""
        # Define schema properties (like Airbyte would provide)
        properties = {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {
                "type": "string",
                "format": "date-time",
                "airbyte_type": "timestamp_without_timezone",
            },
            "metadata": {"type": "object"},
            "score": {"type": "number"},
            "is_active": {"type": "boolean"},
        }

        # Sample records (as they would come from Airbyte)
        records = [
            {
                "id": 1,
                "name": "Alice",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00",
                "metadata": {"role": "admin", "level": 5},
                "score": 95.5,
                "is_active": True,
            },
            {
                "id": 2,
                "name": "Bob",
                "created_at": "2024-01-16T14:45:30.123456+05:00",
                "updated_at": "2024-01-16T14:45:30.123456",
                "metadata": {"role": "user", "tags": ["new", "verified"]},
                "score": 82.0,
                "is_active": False,
            },
            {
                "id": 3,
                "name": "Charlie",
                "created_at": "2024-01-17T08:00:00Z",
                "updated_at": "2024-01-17T08:00:00",
                "metadata": None,
                "score": None,
                "is_active": True,
            },
        ]

        # Convert each record
        fields = []
        converted_rows = [{} for _ in records]

        for field_name, prop in properties.items():
            # Determine type from first non-null value
            sample = next(
                (r.get(field_name) for r in records if r.get(field_name) is not None),
                None,
            )
            pa_type, _ = convert_to_arrow(sample, prop)
            fields.append((field_name, pa_type))

            # Convert all values
            for i, record in enumerate(records):
                _, converted = convert_to_arrow(record.get(field_name), prop)
                converted_rows[i][field_name] = converted

        # Build the PyArrow table
        schema = pa.schema(fields)
        table = pa.Table.from_pylist(converted_rows, schema=schema)

        # Verify the table structure
        assert table.num_rows == 3
        assert table.num_columns == 7

        # Verify column types
        assert table.schema.field("id").type == pa.int64()
        assert table.schema.field("name").type == pa.string()
        assert table.schema.field("created_at").type == pa.timestamp("us", tz="UTC")
        assert table.schema.field("updated_at").type == pa.timestamp("us")
        assert table.schema.field("metadata").type == pa.string()  # JSON serialized
        assert table.schema.field("score").type == pa.float64()
        assert table.schema.field("is_active").type == pa.bool_()

        # Verify some values
        assert table.column("id").to_pylist() == [1, 2, 3]
        assert table.column("name").to_pylist() == ["Alice", "Bob", "Charlie"]
        assert table.column("is_active").to_pylist() == [True, False, True]

        # Verify metadata was JSON serialized
        metadata_values = table.column("metadata").to_pylist()
        assert metadata_values[0] == '{"role": "admin", "level": 5}'
        assert metadata_values[1] == '{"role": "user", "tags": ["new", "verified"]}'
        assert metadata_values[2] is None

        # Verify timestamps are datetime objects (PyArrow will have converted them)
        created_at_values = table.column("created_at").to_pylist()
        assert created_at_values[0].year == 2024
        assert created_at_values[0].month == 1
        assert created_at_values[0].day == 15

    def test_nullable_fields_with_all_nulls(self):
        """Test that fields with all null values still work correctly."""
        properties = {
            "id": {"type": "integer"},
            "optional_timestamp": {"type": ["null", "string"], "format": "date-time"},
        }

        records = [
            {"id": 1, "optional_timestamp": None},
            {"id": 2, "optional_timestamp": None},
        ]

        fields = []
        converted_rows = [{} for _ in records]

        for field_name, prop in properties.items():
            sample = next(
                (r.get(field_name) for r in records if r.get(field_name) is not None),
                None,
            )
            pa_type, _ = convert_to_arrow(sample, prop)
            fields.append((field_name, pa_type))

            for i, record in enumerate(records):
                _, converted = convert_to_arrow(record.get(field_name), prop)
                converted_rows[i][field_name] = converted

        schema = pa.schema(fields)
        table = pa.Table.from_pylist(converted_rows, schema=schema)

        assert table.num_rows == 2
        assert table.column("id").to_pylist() == [1, 2]
        assert table.column("optional_timestamp").to_pylist() == [None, None]
