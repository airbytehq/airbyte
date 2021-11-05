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
import json
import unittest.mock as mock

import pytest
import spec_linter


def test_get_full_field_name():
    assert spec_linter.get_full_field_name("field") == "field"
    assert spec_linter.get_full_field_name("field", ["root"]) == "root.field"
    assert spec_linter.get_full_field_name("field", ["root", "fake_field", "0"]) == "root.fake_field.0.field"


def test_fetch_oneof_schemas():
    # case 1)
    root_schema = {"oneOf": [{"properties": {1: 1}}, {"values": [1, 2, 3]}]}
    schemas = spec_linter.fetch_oneof_schemas(root_schema)
    assert len(schemas) == 1
    assert schemas[0] == {"properties": {1: 1}}
    # case 2)
    root_schema = {"oneOf": [{"properties": {1: 1}}, {"properties": {2: 2}}]}
    schemas = spec_linter.fetch_oneof_schemas(root_schema)
    assert len(schemas) == 2
    assert schemas[0] == {"properties": {1: 1}}
    assert schemas[1] == {"properties": {2: 2}}


@pytest.mark.parametrize(
    "schema,error_text",
    [
        ({"type": "string", "title": "Field"}, "Check failed for field"),
        ({"type": "string", "description": "Format: YYYY-MM-DDTHH:mm:ss[Z]."}, "Check failed for field"),
        (
            {"type": "string", "title": "Field", "description": "Format: YYYY-MM-DDTHH:mm:ss[Z].", "oneOf": "invalid"},
            "Incorrect oneOf schema in field",
        ),
        (
            {
                "type": "string",
                "title": "Field",
                "description": "Format: YYYY-MM-DDTHH:mm:ss[Z].",
                "examples": ["2020-01-01T00:00:00Z"],
                "oneOf": [1, 2, 3],
            },
            "Incorrect oneOf schema in field",
        ),
    ],
)
def test_validate_field(schema, error_text):
    errors = spec_linter.validate_field("field", schema, [])
    assert len(errors) == 1
    assert error_text in errors[0]


def test_validate_field_invalid_schema_and_oneof():
    schema = {
        "type": "string",
        "description": "Format: YYYY-MM-DDTHH:mm:ss[Z].",
        "examples": ["2020-01-01T00:00:00Z"],
        "oneOf": [1, 2, 3],
    }
    errors = spec_linter.validate_field("field", schema, ["root"])
    assert len(errors) == 2
    assert "Check failed for field" in errors[0]
    assert "Incorrect oneOf schema in field" in errors[1]


def test_read_spec_file():
    # file is not json serializable
    with mock.patch("builtins.open", mock.mock_open(read_data="test")):
        assert not spec_linter.read_spec_file("path_1")
    # property field is not exist
    with mock.patch("builtins.open", mock.mock_open(read_data='{"connectionSpecification": "test"}')):
        assert not spec_linter.read_spec_file("path_1")
    # valid schema
    valid_schema = {"connectionSpecification": {"properties": {}}}
    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(valid_schema))):
        assert spec_linter.read_spec_file("path_1")
    # schema with invalid field
    invalid_schema = {"connectionSpecification": {"properties": {"field": {"title": "Field", "type": "string"}}}}
    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(invalid_schema))):
        assert not spec_linter.read_spec_file("path_1")


def test_validate_schema_failed():
    schema = {
        "access_token": {"type": "string", "airbyte_secret": True, "description": "API Key."},
        "store_name": {"type": "string", "title": "Store name."},
        "start_date": {
            "title": "Start Date",
            "type": "string",
            "description": "The date from which you'd like to replicate the data",
            "examples": ["2021-01-01T00:00:00Z"],
        },
    }

    errors = spec_linter.validate_schema("path", schema, ["root"])
    assert len(errors) == 2
    assert "Check failed for field" in errors[0] and "root.access_token" in errors[0]
    assert "Check failed for field" in errors[1] and "root.store_name" in errors[1]


def test_validate_schema_success():
    schema = {
        "access_token": {"type": "string", "airbyte_secret": True, "description": "API Key.", "title": "Key"},
        "store_name": {"type": "string", "description": "My description", "title": "My name"},
        "limit": {
            "title": "Records Limit",
            "type": "integer",
            "description": "Just a limit",
        },
    }

    errors = spec_linter.validate_schema("path", schema, ["root"])
    assert len(errors) == 0


def test_validate_schema_with_nested_oneof():
    schema = {
        "store_name": {"type": "string", "description": "Store name."},
        "start_date": {
            "title": "Start Date",
            "type": "string",
            "description": "The date from which you'd like to replicate the data",
        },
        "nested_field": {
            "type": "object",
            "title": "Nested field title",
            "description": "Nested field description",
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "settings": {
                            "type": "object",
                            "title": "Settings",
                            "description": "blah-blah-blah",
                            "oneOf": [
                                {"type": "object", "properties": {"access_token": {"type": "object"}}},
                                {"type": "string", "multipleOf": 3},
                            ],
                        }
                    },
                },
                {"type": "string", "title": "Start Date"},
            ],
        },
    }

    errors = spec_linter.validate_schema("path", schema, [])
    assert len(errors) == 2
    # check error type
    assert "Check failed for field" == errors[0][0]
    assert "Check failed for field" == errors[1][0]
    # check failed fields
    assert "store_name" == errors[0][1]
    assert "nested_field.0.settings.0.access_token" == errors[1][1]
