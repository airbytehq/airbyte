#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import pytest
from source_hubspot.api import Stream


@pytest.mark.parametrize(
    "field_type,expected",
    [
        ("string", {"type": ["null", "string"]}),
        ("integer", {"type": ["null", "integer"]}),
        ("number", {"type": ["null", "number"]}),
        ("bool", {"type": ["null", "boolean"]}),
        ("boolean", {"type": ["null", "boolean"]}),
        ("enumeration", {"type": ["null", "string"]}),
        ("object", {"type": ["null", "object"]}),
        ("array", {"type": ["null", "array"]}),
        ("date", {"type": ["null", "string"], "format": "date-time"}),
        ("date-time", {"type": ["null", "string"], "format": "date-time"}),
        ("datetime", {"type": ["null", "string"], "format": "date-time"}),
        ("json", {"type": ["null", "string"]}),
        ("phone_number", {"type": ["null", "string"]}),
    ],
)
def test_field_type_format_converting(field_type, expected):
    assert Stream._get_field_props(field_type=field_type) == expected


@pytest.mark.parametrize(
    "field_type,expected",
    [
        ("_unsupported_field_type_", {"type": ["null", "string"]}),
        (None, {"type": ["null", "string"]}),
        (1, {"type": ["null", "string"]}),
    ],
)
def test_bad_field_type_converting(field_type, expected, capsys):

    assert Stream._get_field_props(field_type=field_type) == expected

    logs = capsys.readouterr().out

    assert '"WARN"' in logs
    assert f"Unsupported type {field_type} found" in logs


@pytest.mark.parametrize(
    "declared_field_types,field_name,field_value,casted_value",
    [
        (["null", "string"], "some_field", None, None),
        ("string", "some_field", "test", "test"),
        (["null", "number"], "some_field", "123.456", 123.456),
        (["null", "number"], "user_id", "123", 123),
        (["null", "string"], "some_field", "123", "123"),
        (["null", "string"], "some_field", "", ""),
    ],
)
def test_cast_type_if_needed(declared_field_types, field_name, field_value, casted_value):
    assert Stream._cast_value(declared_field_types, field_name, field_value) == casted_value
