"""Unit tests for utility functions."""

import pytest

from source_tulip.utils import (
    adjust_cursor_for_overlap,
    build_allowed_fields,
    build_api_url,
    build_field_mapping,
    build_tables_url,
    generate_column_name,
    map_tulip_type_to_json_schema,
    transform_record,
)


# --- generate_column_name ---


class TestGenerateColumnName:
    def test_with_label(self):
        assert generate_column_name("rqoqm", "Customer Name") == "customer_name__rqoqm"

    def test_without_label(self):
        assert generate_column_name("rqoqm") == "rqoqm__rqoqm"

    def test_none_label(self):
        assert generate_column_name("rqoqm", None) == "rqoqm__rqoqm"

    def test_empty_label(self):
        assert generate_column_name("rqoqm", "") == "rqoqm__rqoqm"

    def test_whitespace_only_label(self):
        assert generate_column_name("rqoqm", "   ") == "rqoqm__rqoqm"

    def test_special_chars_in_label(self):
        result = generate_column_name("abc", "Hello World! @#$%")
        assert result == "hello_world__abc"

    def test_hyphens_in_label(self):
        result = generate_column_name("xyz", "serial-number")
        assert result == "serial_number__xyz"

    def test_leading_digit_in_label(self):
        result = generate_column_name("abc", "123 Test")
        assert result == "field_123_test__abc"

    def test_leading_digit_in_final_name(self):
        # If field_id starts with digit and no label
        result = generate_column_name("123abc")
        assert result == "field_123abc__123abc"

    def test_multiple_underscores_collapsed(self):
        result = generate_column_name("abc", "hello___world")
        assert result == "hello_world__abc"

    def test_strips_leading_trailing_underscores(self):
        result = generate_column_name("abc", "_test_")
        assert result == "test__abc"

    def test_label_becomes_empty_after_sanitization(self):
        # All special chars => empty label => falls back to field_id
        result = generate_column_name("abc", "!@#$%")
        assert result == "abc__abc"

    def test_mixed_case(self):
        result = generate_column_name("AbCdE", "My Field")
        assert result == "my_field__abcde"


# --- map_tulip_type_to_json_schema ---


class TestMapTulipType:
    def test_integer(self):
        assert map_tulip_type_to_json_schema("integer") == {"type": ["null", "integer"]}

    def test_float(self):
        assert map_tulip_type_to_json_schema("float") == {"type": ["null", "number"]}

    def test_boolean(self):
        assert map_tulip_type_to_json_schema("boolean") == {"type": ["null", "boolean"]}

    def test_timestamp(self):
        result = map_tulip_type_to_json_schema("timestamp")
        assert result == {"type": ["null", "string"], "format": "date-time"}

    def test_datetime(self):
        result = map_tulip_type_to_json_schema("datetime")
        assert result == {"type": ["null", "string"], "format": "date-time"}

    def test_interval(self):
        assert map_tulip_type_to_json_schema("interval") == {
            "type": ["null", "integer"]
        }

    def test_user(self):
        assert map_tulip_type_to_json_schema("user") == {"type": ["null", "string"]}

    def test_unknown_defaults_to_string(self):
        assert map_tulip_type_to_json_schema("foobar") == {"type": ["null", "string"]}

    def test_returns_copy(self):
        """Ensure modifying the return value doesn't affect the original mapping."""
        result1 = map_tulip_type_to_json_schema("integer")
        result1["extra"] = True
        result2 = map_tulip_type_to_json_schema("integer")
        assert "extra" not in result2


# --- build_api_url ---


class TestBuildApiUrl:
    def test_without_workspace(self):
        url = build_api_url("acme", None, "T123", "records")
        assert url == "https://acme.tulip.co/api/v3/tables/T123/records"

    def test_with_workspace(self):
        url = build_api_url("acme", "W456", "T123", "records")
        assert url == "https://acme.tulip.co/api/v3/w/W456/tables/T123/records"

    def test_metadata_endpoint(self):
        url = build_api_url("acme", None, "T123", "")
        assert url == "https://acme.tulip.co/api/v3/tables/T123"

    def test_metadata_with_workspace(self):
        url = build_api_url("acme", "W456", "T123")
        assert url == "https://acme.tulip.co/api/v3/w/W456/tables/T123"


# --- build_tables_url ---


class TestBuildTablesUrl:
    def test_without_workspace(self):
        assert build_tables_url("acme", None) == "https://acme.tulip.co/api/v3/tables"

    def test_with_workspace(self):
        assert (
            build_tables_url("acme", "W456")
            == "https://acme.tulip.co/api/v3/w/W456/tables"
        )


# --- build_field_mapping ---


class TestBuildFieldMapping:
    def test_basic_mapping(self, mock_table_metadata):
        mapping = build_field_mapping(mock_table_metadata)
        assert "field1" in mapping
        assert "field2" in mapping
        assert mapping["field1"] == generate_column_name("field1", "Field One")
        assert mapping["field2"] == generate_column_name("field2", "Field Two")

    def test_excludes_system_fields(self):
        metadata = {
            "columns": [
                {"name": "id", "label": "ID", "dataType": {"type": "string"}},
                {
                    "name": "_createdAt",
                    "label": "Created",
                    "dataType": {"type": "timestamp"},
                },
                {"name": "custom", "label": "Custom", "dataType": {"type": "string"}},
            ]
        }
        mapping = build_field_mapping(metadata)
        assert "id" not in mapping
        assert "_createdAt" not in mapping
        assert "custom" in mapping

    def test_includes_tablelink_in_mapping(self, mock_table_metadata):
        """build_field_mapping doesn't filter tableLink — that's build_allowed_fields' job."""
        mapping = build_field_mapping(mock_table_metadata)
        assert "link1" in mapping

    def test_empty_columns(self):
        mapping = build_field_mapping({"columns": []})
        assert mapping == {}


# --- build_allowed_fields ---


class TestBuildAllowedFields:
    def test_excludes_tablelink(self, mock_table_metadata):
        fields = build_allowed_fields(mock_table_metadata)
        assert "link1" not in fields

    def test_includes_non_tablelink(self, mock_table_metadata):
        fields = build_allowed_fields(mock_table_metadata)
        assert "field1" in fields
        assert "field2" in fields

    def test_always_includes_system_fields(self, mock_table_metadata):
        fields = build_allowed_fields(mock_table_metadata)
        for sys_field in ["id", "_createdAt", "_updatedAt", "_sequenceNumber"]:
            assert sys_field in fields

    def test_no_duplicate_system_fields(self):
        """System fields in columns list shouldn't be duplicated."""
        metadata = {
            "columns": [
                {"name": "id", "label": "ID", "dataType": {"type": "string"}},
                {"name": "custom", "label": "Custom", "dataType": {"type": "string"}},
            ]
        }
        fields = build_allowed_fields(metadata)
        assert fields.count("id") == 1


# --- transform_record ---


class TestTransformRecord:
    def test_maps_custom_fields(self):
        record = {"id": "1", "field1": "val1", "_sequenceNumber": 10}
        mapping = {"field1": "customer_name__field1"}
        result = transform_record(record, mapping)
        assert result["customer_name__field1"] == "val1"
        assert result["id"] == "1"
        assert result["_sequenceNumber"] == 10

    def test_passes_through_unmapped_fields(self):
        record = {"id": "1", "unknown_field": "val"}
        result = transform_record(record, {})
        assert result["unknown_field"] == "val"

    def test_empty_record(self):
        assert transform_record({}, {"a": "b"}) == {}

    def test_serializes_dict_to_json_string(self):
        """Color and other dict values should be serialized to JSON strings."""
        record = {
            "id": "1",
            "color_field": {"r": 0, "g": 0, "b": 0, "a": 1},
        }
        result = transform_record(record, {"color_field": "color__color_field"})
        assert result["color__color_field"] == '{"r": 0, "g": 0, "b": 0, "a": 1}'
        assert isinstance(result["color__color_field"], str)

    def test_serializes_list_to_json_string(self):
        """List values should be serialized to JSON strings."""
        record = {"id": "1", "tags": ["a", "b", "c"]}
        result = transform_record(record, {"tags": "tags__tags"})
        assert result["tags__tags"] == '["a", "b", "c"]'
        assert isinstance(result["tags__tags"], str)

    def test_primitive_values_unchanged(self):
        """String, int, float, bool, None values should pass through unchanged."""
        record = {
            "id": "1",
            "str_field": "hello",
            "int_field": 42,
            "float_field": 3.14,
            "bool_field": True,
            "null_field": None,
        }
        mapping = {
            "str_field": "str__str_field",
            "int_field": "int__int_field",
            "float_field": "float__float_field",
            "bool_field": "bool__bool_field",
            "null_field": "null__null_field",
        }
        result = transform_record(record, mapping)
        assert result["str__str_field"] == "hello"
        assert result["int__int_field"] == 42
        assert result["float__float_field"] == 3.14
        assert result["bool__bool_field"] is True
        assert result["null__null_field"] is None


# --- adjust_cursor_for_overlap ---


class TestAdjustCursorForOverlap:
    def test_subtracts_60_seconds(self):
        result = adjust_cursor_for_overlap("2026-01-01T00:01:00Z")
        assert result == "2026-01-01T00:00:00Z"

    def test_handles_none(self):
        assert adjust_cursor_for_overlap(None) is None

    def test_handles_empty_string(self):
        assert adjust_cursor_for_overlap("") is None

    def test_preserves_z_suffix(self):
        result = adjust_cursor_for_overlap("2026-06-15T12:30:00Z")
        assert result.endswith("Z")

    def test_crosses_midnight(self):
        result = adjust_cursor_for_overlap("2026-01-02T00:00:30Z")
        assert result == "2026-01-01T23:59:30Z"
