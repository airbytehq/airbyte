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

from abc import ABC, abstractmethod
import pytest
from unittest.mock import patch
from source_blob.stream import FileStream, IncrementalFileStream
from airbyte_cdk import AirbyteLogger


LOGGER = AirbyteLogger()


class TestFileStream():

    @pytest.mark.parametrize(  # set return_schema to None for an expected fail
        "schema_string, return_schema",
        [
            (
                "{\"id\": \"integer\", \"name\": \"string\", \"valid\": \"boolean\", \"code\": \"integer\", \"degrees\": \"number\", \"birthday\": \"string\", \"last_seen\": \"string\"}",
                {"id": "integer", "name": "string", "valid": "boolean", "code": "integer", "degrees": "number", "birthday": "string", "last_seen": "string"}
            ),
            ("{\"single_column\": \"boolean\"}", {"single_column": "boolean"}),
            (r"{}", {}),
            ("{this isn't right: \"integer\"}", None),  # invalid json
            ("[ {\"a\":\"b\"} ]", None),  # array instead of object
            ("{\"a\": \"boolean\", \"b\": {\"string\": \"integer\"}}", None),  # object as a value
            ("{\"a\": [\"boolean\", \"string\"], \"b\": {\"string\": \"integer\"}}", None),  # array and object as values
            ("{\"a\": \"integer\", \"b\": \"NOT A REAL DATATYPE\"}", None),  # incorrect datatype
            ("{\"a\": \"NOT A REAL DATATYPE\", \"b\": \"ANOTHER FAKE DATATYPE\"}", None)  # multiple incorrect datatypes
        ]
    )
    def test_init_schema(self, schema_string, return_schema):
        if return_schema is not None:
            assert FileStream._init_schema(schema_string) == return_schema
        else:
            with pytest.raises(Exception) as e_info:
                FileStream._init_schema(schema_string)

    @pytest.mark.parametrize(  # set expected_return_record to None for an expected fail
        "target_columns, record, expected_return_record",
        [
            (  # simple case
                ["id", "first_name", "last_name"],
                {"id":"1", "first_name":"Frodo", "last_name":"Baggins"},
                {"id":"1", "first_name":"Frodo", "last_name":"Baggins", "_airbyte_additional_properties": {}}
            ),
            (  # additional columns
                ["id", "first_name", "last_name"],
                {"id":"1", "first_name":"Frodo", "last_name":"Baggins", "location":"The Shire", "items":["The One Ring", "Sting"]},
                {"id":"1", "first_name":"Frodo", "last_name":"Baggins", "_airbyte_additional_properties": {"location":"The Shire", "items":["The One Ring", "Sting"]}}
            ),
            (  # missing columns
                ["id", "first_name", "last_name", "location", "items"],
                {"id":"1", "first_name":"Frodo", "last_name":"Baggins"},
                {"id":"1", "first_name":"Frodo", "last_name":"Baggins", "location":None, "items":None, "_airbyte_additional_properties": {}}
            ),
            (  # additional and missing columns
                ["id", "first_name", "last_name", "friends", "enemies"],
                {"id":"1", "first_name":"Frodo", "last_name":"Baggins", "location":"The Shire", "items":["The One Ring", "Sting"]},
                {"id":"1", "first_name":"Frodo", "last_name":"Baggins", "friends":None, "enemies":None, "_airbyte_additional_properties": {"location":"The Shire", "items":["The One Ring", "Sting"]}}
            ),
        ]
    )
    @patch("source_blob.stream.FileStream.__abstractmethods__", set())  # patching abstractmethods to empty set so we can instantiate ABC to test
    def test_match_target_schema(self, target_columns, record, expected_return_record):
        fs = FileStream(dataset_name='dummy', provider={}, format={}, path_patterns=[])
        if expected_return_record is not None:
            assert fs._match_target_schema(record, target_columns) == expected_return_record
        else:
            with pytest.raises(Exception) as e_info:
                fs._match_target_schema(record, target_columns)

    @pytest.mark.parametrize(  # set expected_return_record to None for an expected fail
        "extra_map, record, expected_return_record",
        [
            (  # one extra field
                {"friend": "Frodo"},
                {"id":"1", "first_name":"Samwise", "last_name":"Gamgee"},
                {"id":"1", "first_name":"Samwise", "last_name":"Gamgee", "friend": "Frodo"}
            ),
            (  # multiple extra fields
                {"friend": "Frodo", "enemy": "Gollum", "loves": "PO-TAY-TOES"},
                {"id":"1", "first_name":"Samwise", "last_name":"Gamgee"},
                {"id":"1", "first_name":"Samwise", "last_name":"Gamgee", "friend": "Frodo", "enemy": "Gollum", "loves": "PO-TAY-TOES"}
            ),
            (  # empty extra_map
                {},
                {"id":"1", "first_name":"Samwise", "last_name":"Gamgee"},
                {"id":"1", "first_name":"Samwise", "last_name":"Gamgee"}
            ),
        ]
    )
    @patch("source_blob.stream.FileStream.__abstractmethods__", set())  # patching abstractmethods to empty set so we can instantiate ABC to test
    def test_add_extra_fields_from_map(self, extra_map, record, expected_return_record):
        fs = FileStream(dataset_name='dummy', provider={}, format={}, path_patterns=[])
        if expected_return_record is not None:
            assert fs._add_extra_fields_from_map(record, extra_map) == expected_return_record
        else:
            with pytest.raises(Exception) as e_info:
                fs._add_extra_fields_from_map(record, extra_map)
