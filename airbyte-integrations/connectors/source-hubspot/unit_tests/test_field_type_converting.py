import pytest
from source_hubspot.api import Stream


@pytest.mark.parametrize("field_type,expected", [
    ("string", {"type": "string"}),
    ("integer", {"type": "integer"}),
    ("number", {"type": "number"}),
    ("bool", {"type": "boolean"}),
    ("boolean", {"type": "boolean"}),
    ("enumeration", {"type": "string"}),
    ("object", {"type": "object"}),
    ("array", {"type": "array"}),
    ("date", {"type": "string", "format": "date-time"}),
    ("date-time", {"type": "string", "format": "date-time"}),
    ("datetime", {"type": "string", "format": "date-time"}),
    ("json", {"type": "string"}),
    ("phone_number", {"type": "string"}),
])
def test_field_type_format_converting(field_type, expected):
    assert Stream._get_field_props(field_type=field_type) == expected


@pytest.mark.parametrize("field_type,expected", [
    ("_unsupported_field_type_", {"type": "_unsupported_field_type_"}),
    (None, {"type": None}),
    (1, {"type": 1}),
])
def test_bad_field_type_converting(field_type, expected, capsys):

    assert Stream._get_field_props(field_type=field_type) == {"type": field_type}

    logs = capsys.readouterr().out

    assert '"WARN"' in logs
    assert f'Unsupported type {field_type} found' in logs
